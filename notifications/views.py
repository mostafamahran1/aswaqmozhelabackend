from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status

from .models import AppRelease, CustomerPresence, InboxNotice, NoticeRead
from .services import send_to_topics

AUDIENCES = {
    'customers': ['customers'],
    'staff': ['staff'],
    'admins': ['admins'],
    'all': ['customers', 'staff', 'admins'],
}


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customer_presence(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        return Response({'sent': False})

    presence, _ = CustomerPresence.objects.get_or_create(user=user)
    if not presence.should_notify():
        return Response({'sent': False})

    name = user.get_full_name().strip() or user.username
    sent = send_to_topics(
        ['admins'],
        'عميل دخل التطبيق',
        name,
        {'type': 'presence', 'user_id': user.id},
    )
    if sent:
        presence.mark_notified()
    return Response({'sent': sent})


@api_view(['GET'])
@permission_classes([AllowAny])
def app_release(request):
    release = AppRelease.objects.order_by('-build_number', '-created_at').first()
    if release is None:
        return Response({'build_number': 0})
    return Response({
        'version_name': release.version_name,
        'build_number': release.build_number,
        'title': release.title,
        'message': release.message,
        'store_url': release.store_url,
    })


@api_view(['POST'])
@permission_classes([IsSuperuser])
def publish_app_release(request):
    version_name = str(request.data.get('version_name', '')).strip()
    try:
        build_number = int(request.data.get('build_number'))
    except (TypeError, ValueError):
        build_number = 0
    if not version_name or build_number < 1:
        return Response(
            {'error': 'version_name and build_number are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    release = AppRelease.objects.create(
        version_name=version_name[:20],
        build_number=build_number,
        title=str(request.data.get('title') or 'تحديث جديد').strip()[:120],
        message=str(
            request.data.get('message')
            or 'في تحديث جديد للتطبيق. نزّله دلوقتي عشان تستخدم آخر نسخة.'
        ).strip(),
        store_url=str(request.data.get('store_url') or '').strip(),
    )
    return Response({
        'id': release.id,
        'version_name': release.version_name,
        'build_number': release.build_number,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsSuperuser])
def announce(request):
    audience = request.data.get('audience', 'customers')
    title = str(request.data.get('title', '')).strip()
    body = str(request.data.get('body', '')).strip()
    topics = AUDIENCES.get(audience)
    if topics is None or not title or not body:
        return Response(
            {'error': 'title, body, and a valid audience are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    sent = send_to_topics(topics, title, body, {'type': 'announcement'})
    return Response({'sent': sent})


def _audience_for(user):
    if not user.is_authenticated:
        return 'customers'
    if user.is_superuser:
        return 'admins'
    if user.is_staff:
        return 'staff'
    return 'customers'


def _notice_data(notice, is_read):
    return {
        'id': notice.id,
        'title': notice.title,
        'body': notice.body,
        'kind': notice.kind,
        'payload': notice.payload or {},
        'created_at': notice.created_at.isoformat(),
        'is_read': is_read,
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def inbox(request):
    audience = _audience_for(request.user)
    notices = list(
        InboxNotice.objects.filter(audience=audience).order_by('-created_at')[:50]
    )
    read_ids = set()
    unread_count = len(notices)
    if request.user.is_authenticated:
        read_ids = set(
            NoticeRead.objects.filter(
                user=request.user,
                notice__audience=audience,
            ).values_list('notice_id', flat=True)
        )
        unread_count = InboxNotice.objects.filter(audience=audience).exclude(
            id__in=read_ids
        ).count()
    return Response({
        'unread_count': unread_count,
        'results': [
            _notice_data(notice, notice.id in read_ids)
            for notice in notices
        ],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_inbox_read(request):
    audience = _audience_for(request.user)
    notices = InboxNotice.objects.filter(audience=audience)
    if not request.data.get('all'):
        raw_ids = request.data.get('ids') or []
        ids = []
        for value in raw_ids:
            try:
                ids.append(int(value))
            except (TypeError, ValueError):
                continue
        notices = notices.filter(id__in=ids)
    already = set(
        NoticeRead.objects.filter(
            user=request.user,
            notice__in=notices,
        ).values_list('notice_id', flat=True)
    )
    NoticeRead.objects.bulk_create(
        [
            NoticeRead(user=request.user, notice_id=notice_id)
            for notice_id in notices.exclude(id__in=already).values_list('id', flat=True)
        ],
        ignore_conflicts=True,
    )
    return Response({'ok': True})
