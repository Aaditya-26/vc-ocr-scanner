import os
import uuid

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from PIL import Image, UnidentifiedImageError
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContactMaster
from .ocr_service import process_visiting_card
from .serializers import ContactSerializer, ContactUpdateSerializer

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}


# ─── HTML page views ────────────────────────────────────────────────────────
def dashboard(request):
    return render(request, 'vc_app/index.html')


def upload_page(request):
    return render(request, 'vc_app/upload.html')


def detail_page(request, pk):
    return render(request, 'vc_app/detail.html', {'contact_id': pk})


# ─── REST API views ─────────────────────────────────────────────────────────

class VisitingCardUploadView(APIView):
    """POST /api/v1/visiting-card/upload/"""
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('image')
        if not file:
            return Response({'error': 'No image file provided.'}, status=400)

        ext = file.name.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Response(
                {'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'},
                status=400,
            )

        filename = f'{uuid.uuid4()}.{ext}'
        save_dir = os.path.join(settings.MEDIA_ROOT, 'vc_images')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        with open(save_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        # verify the file is actually a valid image, not just a renamed binary
        if ext != 'pdf':
            try:
                with Image.open(save_path) as img:
                    img.verify()
            except (UnidentifiedImageError, Exception):
                os.remove(save_path)
                return Response({'error': 'File is not a valid image.'}, status=400)

        # Run OCR
        try:
            data = process_visiting_card(save_path)
        except Exception as exc:
            # clean up saved file on OCR failure to avoid disk leaks
            os.remove(save_path)
            return Response({'error': f'OCR failed: {str(exc)}'}, status=500)

        email = data.get('email')
        mobile = data.get('mobile')
        is_dup = False
        if email or mobile:
            q = Q()
            if email:
                q |= Q(email=email)
            if mobile:
                q |= Q(mobile=mobile)
            is_dup = ContactMaster.objects.filter(q).exists()

        rel_path = os.path.join('vc_images', filename)

        contact = ContactMaster.objects.create(
            name=data.get('name') or 'Unknown',
            designation=data.get('designation'),
            company_name=data.get('company'),
            mobile=mobile,
            email=email,
            website=data.get('website'),
            address=data.get('address'),
            raw_text=data['raw_text'],
            confidence_score=data['ocr_confidence'],
            image_path=rel_path,
            is_duplicate=is_dup,
        )
        return Response(ContactSerializer(contact).data, status=201)


class ContactListView(APIView):
    """GET /api/v1/contacts/"""

    def get(self, request):
        contacts = ContactMaster.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response({
            'count': contacts.count(),
            'results': serializer.data,
        })


class ContactDetailView(APIView):
    """GET /api/v1/contact/<id>/   PUT /api/v1/contact/<id>/"""

    def get(self, request, pk):
        contact = get_object_or_404(ContactMaster, pk=pk)
        return Response(ContactSerializer(contact).data)

    def put(self, request, pk):
        contact = get_object_or_404(ContactMaster, pk=pk)
        serializer = ContactUpdateSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # refresh so updated_at and any other auto fields are current in the response
            contact.refresh_from_db()
            return Response(ContactSerializer(contact).data)
        return Response(serializer.errors, status=400)


class ContactDeleteView(APIView):
    """DELETE /api/v1/contact/<id>/delete/"""

    def delete(self, request, pk):
        contact = get_object_or_404(ContactMaster, pk=pk)
        contact.delete()
        # 204 No Content is the correct REST status for a successful delete
        return Response(status=status.HTTP_204_NO_CONTENT)