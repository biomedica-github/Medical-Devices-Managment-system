from typing import Any
from django.shortcuts import get_object_or_404
from inventario.models import Proveedor, Contrato, Equipo_medico, Area_hospital, Orden_Servicio, Cama, ReporteUsuario, CheckList
from django.http import HttpResponse
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProveedorSerializers, ContratoSerializers, Equipo_Serializer, AreaSerializer, OrdenEquipoSerializer, OrdenAgendaSerializer, AgregarEquipoAreaSerializer
from . import serializers
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from django.db.models import Q
from .permissions import IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from datetime import date

class ProveedorViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Proveedor.objects.prefetch_related('proveedor_contrato').all()
    serializer_class = ProveedorSerializers
    lookup_field = 'id'

    

class ContratoViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Contrato.objects.select_related('proveedor').prefetch_related('equipos_contrato','equipos_contrato__area').all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearContratoSerializer
        return ContratoSerializers

    def get_serializer_context(self):
        return {'request': self.request}

class EquipoViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearEquipoSerializer
        return Equipo_Serializer

    queryset = Equipo_medico.objects.select_related('contrato','area','cama').all()

    def get_serializer_context(self):
        return {'request': self.request}

class CamaViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminOrReadOnly()]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.GetCamaSerializer
        elif self.request.method == 'PUT':
            return serializers.PutCamaSerializer
        return serializers.CrearCamaSerializer
    

    def get_serializer_context(self):
        if 'pk' in self.kwargs.keys():
            return {'area': self.kwargs['id_pk'], 'cama': self.kwargs['pk']}
        return {'area': self.kwargs['id_pk']}

    def get_queryset(self):
        return Cama.objects.select_related('sala').prefetch_related('equipos_cama').filter(sala__responsable = self.request.user.id)

class CheckListViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.CheckListSerializer

    queryset = CheckList.objects.select_related('area','equipo').all()


class LevantarMultipleCheckList(ModelViewSet):
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearCheckListGeneralSerializer
        return serializers.CheckListSerializer

    queryset = CheckList.objects.prefetch_related('area', 'equipo').all()


class CheckListEspecificoViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearCheckListSerializer
        return serializers.CheckListSerializer


    def get_serializer_context(self):
        sala = Equipo_medico.objects.values('area').get(numero_nacional_inv=self.kwargs['equipo_pk'])
        return {'equipo': self.kwargs['equipo_pk'], 'area': sala['area']}


    def get_queryset(self):
        return CheckList.objects.prefetch_related('area','equipo').filter(equipo=self.kwargs['equipo_pk'])

class CheckListCrearViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = serializers.CrearCheckListSerializer
    def get_serializer_context(self):
        
        return {'area': self.kwargs['id_pk'], 'equipo': self.kwargs['area_equipo_pk'] }
    
class CrearReporteViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CrearReporteSerializer

    def create(self, request, *args, **kwargs):
        equipo = Equipo_medico.objects.filter(area__responsable = request.user.id, numero_nacional_inv = kwargs['area_equipo_pk'])
        if equipo:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            id = serializer.data['id']
            return Response(f'Su ID de reporte es: {id}', status=status.HTTP_201_CREATED, headers=headers)
        return Response('Usuario Incorrecto')

    def get_queryset(self):
        return ReporteUsuario.objects.filter(area = self.kwargs['id_pk'], area__responsable = self.request.user.id)

    def get_serializer_context(self):
        contexto = {'area': self.kwargs['id_pk'], 'equipo': self.kwargs['area_equipo_pk'], 'usuario': self.request.user.id}

        return {'area': self.kwargs['id_pk'], 'equipo': self.kwargs['area_equipo_pk'], 'usuario': self.request.user.id}
    
class AreaViewSet(ModelViewSet):

    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return AgregarEquipoAreaSerializer
        return AreaSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminOrReadOnly()]

    def get_queryset(self):
        return Area_hospital.objects.prefetch_related('equipos_area', 'responsable').filter(responsable = self.request.user.id)
    
    @action(detail=False, methods= ['GET'])
    def servicio(self, request):
        orden = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__area__responsable = request.user.id).exclude(tipo_orden='A').all()
        serializer = OrdenEquipoSerializer(orden, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def agenda(self, request):
        orden = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__area__responsable = request.user.id, tipo_orden = 'A').all()
        serializer = OrdenAgendaSerializer(orden, many=True)
        return Response(serializer.data)

class AgendaUsuarioViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = OrdenAgendaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        today = date.today()
        return Orden_Servicio.objects.prefetch_related('equipo_medico').\
        filter(equipo_medico__area__responsable = self.request.user.id, tipo_orden = 'A', fecha__gte=today).order_by('fecha').all()


class CrearOrdenViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearOrdenSerializer
        return OrdenEquipoSerializer
    queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').exclude(estatus="PEN").order_by('-fecha').all()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
class AreaEquipoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    
    def get_serializer_class(self):
        return serializers.AreaEquipoSerializer
    
    def get_queryset(self):
        return Equipo_medico.objects.select_related('area').filter(area=self.kwargs['id_pk'], area__responsable = self.request.user.id)


class AgendaAreaViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = OrdenAgendaSerializer

    def get_queryset(self):
        return Orden_Servicio.objects.prefetch_related('equipo_medico', 'equipo_medico__area').filter(tipo_orden='A', equipo_medico__numero_nacional_inv = self.kwargs['area_equipo_pk']
                                                                                                      ,equipo_medico__area__responsable = self.request.user.id)

    def get_serializer_context(self):
        print(self.kwargs)
        return {'equipo': self.kwargs['area_equipo_pk']}

class AreaOrdenesViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = OrdenEquipoSerializer
    
    def get_queryset(self):
        queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__numero_nacional_inv=self.kwargs['equipo_pk'])
        return queryset


class OrdenViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AgregarServicioEquipo
        return OrdenEquipoSerializer
    
    def get_queryset(self):
        queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__numero_nacional_inv=self.kwargs['equipo_pk'])
        return queryset
    
    def get_serializer_context(self):
        return {'equipo': self.kwargs['equipo_pk']}

class AgendaAdminViewset(ModelViewSet):
    
    permission_classes = [IsAdminUser]
    today = date.today()
    serializer_class = serializers.AgendaAdminSerializer
    
    #def get_serializer_class(self):
    
     #   if self.request.method == 'POST' or self.request.method == 'PUT':
      #      return serializers.AgregarAgendaAdminSerializer
       # return serializers.AgendaAdminSerializer

    queryset = Orden_Servicio.objects.prefetch_related('equipo_medico', 'equipo_medico__area').filter(tipo_orden='A', fecha__gte=today).order_by('fecha').all()





class AgendaViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = OrdenAgendaSerializer
    
    def get_queryset(self):
        return Orden_Servicio.objects.prefetch_related('equipo_medico', 'equipo_medico__area').filter(tipo_orden='A', equipo_medico__numero_nacional_inv = self.kwargs['equipo_pk'])

    def get_serializer_context(self):
        return {'equipo': self.kwargs['equipo_pk']}

class VerReportesViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser]
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return serializers.AtenderReporteSerializer
        return serializers.VerReportesSerializer

    queryset = ReporteUsuario.objects.select_related('area', 'equipo').all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response('Reporte actualizado exitosamente')

class VerReportesPendientesViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return serializers.AtenderReporteSerializer
        return serializers.VerReportesSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response('Reporte actualizado exitosamente')

    queryset = ReporteUsuario.objects.select_related('area', 'equipo').filter(estado="PEN")

class VerReportesCompletadosViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser]
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return serializers.AtenderReporteSerializer
        return serializers.VerReportesSerializer
    

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response('Reporte actualizado exitosamente')

    queryset = ReporteUsuario.objects.select_related('area', 'equipo').filter(estado="COM")
    