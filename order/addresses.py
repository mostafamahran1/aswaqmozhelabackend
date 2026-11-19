from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import DeliveryGovernorate, SavedAddress


def _clean(value, limit):
    return str(value or '').strip()[:limit]


def _payload(address):
    return {
        'id': address.id,
        'label': address.label,
        'phone_no': address.phone_no,
        'governorate': address.governorate,
        'city': address.city,
        'street': address.street,
        'country': address.country,
        'is_default': address.is_default,
    }


def _read_fields(data):
    phone = ''.join(ch for ch in _clean(data.get('phone_no'), 20) if ch.isdigit())
    governorate = _clean(data.get('governorate'), 100)
    city = _clean(data.get('city'), 200)
    street = _clean(data.get('street'), 500)
    country = _clean(data.get('country'), 100) or 'مصر'
    label = _clean(data.get('label'), 40) or 'البيت'
    if len(phone) < 10 or len(phone) > 15:
        return None, 'اكتب رقم موبايل صحيح.'
    if not governorate or not city or not street:
        return None, 'المحافظة والمدينة والشارع مطلوبين.'
    if not DeliveryGovernorate.objects.filter(name=governorate).exists():
        return None, 'اختار محافظة من القائمة.'
    return {
        'label': label,
        'phone_no': phone,
        'governorate': governorate,
        'city': city,
        'street': street,
        'country': country,
    }, None


def _owned(user):
    return SavedAddress.objects.filter(user=user)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def addresses(request):
    if request.method == 'GET':
        return Response({
            'addresses': [_payload(item) for item in _owned(request.user)],
        })

    fields, error = _read_fields(request.data)
    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        type(request.user).objects.select_for_update().get(pk=request.user.pk)
        make_default = bool(request.data.get('is_default')) or not _owned(request.user).exists()
        if make_default:
            _owned(request.user).filter(is_default=True).update(is_default=False)
        address = SavedAddress.objects.create(
            user=request.user,
            is_default=make_default,
            **fields,
        )
    return Response(_payload(address), status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def address_detail(request, pk):
    address = _owned(request.user).filter(pk=pk).first()
    if address is None:
        return Response({'error': 'العنوان مش موجود.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        with transaction.atomic():
            was_default = address.is_default
            address.delete()
            if was_default:
                replacement = _owned(request.user).order_by('-created_at').first()
                if replacement is not None:
                    replacement.is_default = True
                    replacement.save(update_fields=['is_default'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    fields, error = _read_fields({**_payload(address), **request.data})
    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        type(request.user).objects.select_for_update().get(pk=request.user.pk)
        make_default = bool(request.data.get('is_default', address.is_default))
        if make_default:
            _owned(request.user).exclude(pk=address.pk).filter(is_default=True).update(is_default=False)
        elif address.is_default and not _owned(request.user).exclude(pk=address.pk).exists():
            make_default = True
        elif address.is_default and not make_default:
            replacement = _owned(request.user).exclude(pk=address.pk).order_by('-created_at').first()
            if replacement is not None:
                replacement.is_default = True
                replacement.save(update_fields=['is_default'])
        for key, value in fields.items():
            setattr(address, key, value)
        address.is_default = make_default
        address.save()
    return Response(_payload(address))
