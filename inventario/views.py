from typing import Any
from django.shortcuts import get_object_or_404
from inventario.models import Proveedor, Contrato, Equipo_medico, Area_hospital, Orden_Servicio, ReporteUsuario, CheckList
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
from rest_framework import filters, renderers
from  django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination, _get_displayed_page_numbers
from datetime import date
from . import filters as filtros
from django.views.generic import ListView
from django.core.paginator import Paginator

from rest_framework.templatetags import rest_framework as template123


class ProveedorViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Proveedor.objects.prefetch_related('proveedor_contrato').all()
    serializer_class = ProveedorSerializers
    lookup_field = 'id'
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'interfaz/Proveedor/Proveedores-general.html'
    pagination_class = PageNumberPagination
    
    filterset_class = filtros.filtro_proveedor
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'contenido':serializer.data, 'serializer':serializer}, template_name='interfaz/Proveedor/Proveedor-especifico.html')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_paginated_response(self, data):
        pagination = self.paginator.get_paginated_response(data)
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'content': data, 'paginator': self.paginator, 'serializer':serializer})
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data":serializer.data, "serializer":serializer}, template_name= 'interfaz/Proveedor/Proveedor-especifico.html' )
    
    @action(detail=True, methods=['post'], serializer_class = serializers.AgregarContratoProveedorSerializer)
    def agregar_contrato(self, request, id):
        objeto = self.get_object()
        proveedor_id = objeto.id
        serializer = serializers.AgregarContratoProveedorSerializer(data=request.data, context={'proveedor': proveedor_id})
        if serializer.is_valid():
            proveedor_objeto = Proveedor.objects.get(id = id)
            contrato_nuevo = Contrato.objects.create(proveedor=proveedor_objeto, **serializer.validated_data)
            contrato_nuevo.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContratoViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Contrato.objects.select_related('proveedor').prefetch_related('equipos_contrato','equipos_contrato__area').all()
    filterset_class = filtros.filtro_contrato
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'interfaz/Contratos/contratos-general.html'

    def get_paginated_response(self, data):
        return Response({'content': data, 'paginator': self.paginator})

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, template_name='interfaz/Contratos/contratos-especifico.html')
    
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearContratoSerializer
        return ContratoSerializers

    def get_serializer_context(self):
        return {'request': self.request}

class EquipoViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    filterset_class = filtros.filtro_equipo
    
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearEquipoSerializer
        return Equipo_Serializer

    queryset = Equipo_medico.objects.select_related('contrato','area').all()

    def get_serializer_context(self):
        return {'request': self.request}

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
    filterset_class = filtros.filtro_equipo_checklist

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
    

class CrearOrdenAreaViewset(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = serializers.AgregarServicioEquipo

    def get_serializer_context(self):
        
        return {'equipo': self.kwargs['area_equipo_pk']}
        
    
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
    filterset_class = filtros.filtro_areas_general

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
    
    @action(detail=True, methods= ['GET'])
    def servicio(self, request, pk):
        orden = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__area__responsable = request.user.id, equipo_medico__area=pk).exclude(tipo_orden='A', estatus='PEN').all()
        serializer = OrdenEquipoSerializer(orden, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def agenda(self, request, pk):
        salas_permitidas = Area_hospital.objects.values('nombre_sala').get(id=pk)
        orden = Orden_Servicio.objects.prefetch_related('equipo_medico', 'equipo_medico__area').filter(equipo_medico__area__responsable = request.user.id, tipo_orden = 'A', equipo_medico__area=pk).all()
        serializer = serializers.OrdenAgendaAreaUsuarioVerSerializer(orden, many=True)
        for i in serializer.data:
            lista_equipos_locales = []
            for j in enumerate(i['equipo_medico']):
                if j[1]['area'] in salas_permitidas['nombre_sala']:
                    lista_equipos_locales.append(j[1])
            i['equipo_medico'].clear()
            [i['equipo_medico'].append(key) for key in lista_equipos_locales]               
                
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
    filterset_class = filtros.filtro_ordenservicio
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.CrearOrdenSerializer
        return OrdenEquipoSerializer
    queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').exclude(estatus="PEN").order_by('-fecha').all()


class OrdenPendientesViewSet(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser]
    filterset_class = filtros.filtro_ordenpendiente
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return serializers.CrearOrdenSerializer
        return OrdenEquipoSerializer
    queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(estatus='PEN').order_by('-fecha').all()


class AreaEquipoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    filterset_class = filtros.filtro_areas_equipo

    

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return serializers.CrearEquipoSerializer
        return serializers.AreaEquipoSerializer
    
    def get_queryset(self):
        return Equipo_medico.objects.select_related('area').filter(area=self.kwargs['id_pk'], area__responsable = self.request.user.id)


class AgendaAreaViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    serializer_class = OrdenAgendaSerializer
    filterset_class = filtros.filtro_equipo_agenda
    def get_queryset(self):
        return Orden_Servicio.objects.prefetch_related('equipo_medico', 'equipo_medico__area').filter(tipo_orden='A', equipo_medico__numero_nacional_inv = self.kwargs['area_equipo_pk']
                                                                                                      ,equipo_medico__area__responsable = self.request.user.id)

    def get_serializer_context(self):
        return {'equipo': self.kwargs['area_equipo_pk']}

class AreaAgendaViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = filtros.filtro_agenda

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return serializers.AgregarOrdenAgendaAreaSerializer
        return serializers.OrdenAgendaAreaSerializer

    def get_queryset(self):
        return Orden_Servicio.objects.prefetch_related('equipo_medico', 
                                                              'equipo_medico__area')\
                                                                .filter(tipo_orden='A', equipo_medico__area = self.kwargs['id_pk']\
                                                                    ,equipo_medico__area__responsable = self.request.user.id)


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
    
    filterset_class = filtros.filtro_equipo_servicio
    
    
    def get_queryset(self):
        queryset = Orden_Servicio.objects.prefetch_related('equipo_medico').filter(equipo_medico__numero_nacional_inv=self.kwargs['equipo_pk']).exclude(numero_orden = None)
        return queryset
    
    def get_serializer_context(self):
        return {'equipo': self.kwargs['equipo_pk']}

class AgendaAdminViewset(ModelViewSet):
    
    permission_classes = [IsAdminUser]
    filterset_class = filtros.filtro_agenda
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
    filterset_class = filtros.filtro_equipo_agenda
    
    def get_queryset(self):
        return Orden_Servicio.objects.prefetch_related('equipo_medico', 'equipo_medico__area').filter(tipo_orden='A', equipo_medico__numero_nacional_inv = self.kwargs['equipo_pk'], estatus='PEN')

    def get_serializer_context(self):
        return {'equipo': self.kwargs['equipo_pk']}

class VerReportesViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser]
    filterset_class = filtros.filtro_reportes
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
    filterset_class = filtros.filtro_reportes
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return serializers.AtenderReporteSerializer
        return serializers.VerReportesSerializer
        
    
    def get_serializer_context(self):
        if 'pk' in self.kwargs:
            return {'ticket':self.kwargs['pk']}
        return 
    
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
    filterset_class = filtros.filtro_reportes
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return serializers.AtenderReporteSerializer
        elif self.request.method == 'POST':
            return serializers.AgregarServicioEquipo
        return serializers.VerReportesSerializer
    
    @action(detail=True, methods= ['post'])
    def servicio(self, request, pk):
        ticket = self.get_object()
        equipo = ticket.equipo.numero_nacional_inv
        serializer = serializers.AgregarServicioEquipo(data=request.data, context={'equipo': equipo})
        if serializer.is_valid():
            orden_creada = Orden_Servicio.objects.create(**serializer.validated_data)
            ticket.orden = orden_creada
            ticket.save()
            return  Response({'Mensaje':'Orden creada satisfactoriamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
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
    