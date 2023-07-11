from django.db import models


class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, null=True)

class Contrato(models.Model):
    CONTRATO_CONSOLIDADO = 'C'
    CONTRATO_GARANTIA = 'G'
    CONTRATO_LOCAL = 'L'
    CONTRATO_OPCIONES = [
        (CONTRATO_LOCAL, 'Contrato local'),
        (CONTRATO_GARANTIA, 'Contrato garantia'),
        (CONTRATO_CONSOLIDADO, 'Contrato consolidado')
    ]
    SERVICIO_PREVENTIVO = 'PRV'
    SERVICIO_PREV_CORR = 'P/C'
    NO_SERVICIO = 'N/A'
    SERVICIO_OPCIONES = [
        (SERVICIO_PREV_CORR, 'Servicio preventivo y correctivo'),
        (SERVICIO_PREVENTIVO, 'Servicio  preventivo'),
        (NO_SERVICIO, 'Proveedor no brinda servicio')
    ]
    num_contrato = models.CharField(max_length=100, primary_key=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    tipo_contrato = models.CharField(max_length=1, choices=CONTRATO_OPCIONES, default=CONTRATO_LOCAL)
    tipo_servicio_estipulado = models.CharField(max_length=3, choices=SERVICIO_OPCIONES, default=SERVICIO_PREVENTIVO)
    fecha_vencimiento = models.DateField(auto_now=False, auto_now_add=False)
    num_servicios = models.PositiveIntegerField()

class Especialidad(models.Model):
    nombre_especialidad = models.CharField(max_length=50)

class Sala_hospital(models.Model):
    numero_sala = models.PositiveIntegerField()
    encargado = models.CharField(max_length=100)
    nombre_sala = models.CharField(max_length=100)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True)

class Cama(models.Model):
    numero_cama = models.PositiveIntegerField(primary_key=True)
    sala = models.ForeignKey(Sala_hospital, on_delete=models.PROTECT)

class Equipo_medico(models.Model):
    numero_nacional_inv = models.CharField(max_length= 100, primary_key=True)
    nombre_equipo = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    observaciones = models.CharField(max_length=255, null=True)
    numero_serie = models.CharField(max_length=255, null=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50, null=True)
    cama = models.OneToOneField(Cama, on_delete=models.SET_NULL, null= True)
    contrato = models.ForeignKey(Contrato, on_delete=models.SET_NULL, null=True)

class Orden_Servicio(models.Model):
    MOTIVO_CORRECTIVO = 'C'
    MOTIVO_PREVENTIVO = 'P'
    MOTIVO_REFACCION = 'R'
    MOTIVO_DIAGNOSTICO = 'D'
    MOTIVO_OPCIONES = [
        (MOTIVO_CORRECTIVO, 'Correctivo'),
        (MOTIVO_PREVENTIVO, 'Preventivo'),
        (MOTIVO_DIAGNOSTICO, 'Diagnostico'),
        (MOTIVO_REFACCION, 'Refaccion')
    ]
    
    TIPO_AGENDADA = 'A'
    TIPO_ESPONTANEA = 'E'
    TIPO_BITACORA = 'B'
    TIPO_OPCIONES = [
        (TIPO_AGENDADA, 'Orden agendada'),
        (TIPO_ESPONTANEA, 'Orden espontanea'),
        (TIPO_BITACORA, 'Bitacora mensual')
    ]

    ESTATUS_FUERA = 'OUT'
    ESTATUS_FUNCIONAL = 'FUN'
    ESTATUS_NO_SERVICIO = 'N/A'
    ESTATUS_OPCIONES = [
        (ESTATUS_FUNCIONAL, 'Equipo funcional'),
        (ESTATUS_FUERA, 'Equipo fuera de servicio'),
        (ESTATUS_NO_SERVICIO, 'No se realizo servicio')
    ]

    numero_orden = models.CharField(max_length=255)
    fecha = models.DateField(auto_now_add=False, auto_now=False)
    motivo = models.CharField(max_length=1, choices=MOTIVO_OPCIONES, default=MOTIVO_PREVENTIVO)
    tipo_orden = models.CharField(max_length=1, choices=TIPO_OPCIONES, default=TIPO_ESPONTANEA)
    estatus = models.CharField(max_length=3, choices=ESTATUS_OPCIONES, default=ESTATUS_FUNCIONAL)
    responsable = models.CharField(max_length=100)
    autorizo_jefe_biomedica = models.BooleanField()
    autorizo_jefe_conservacion = models.BooleanField()
    orden_escaneada = models.FileField(null=True)
    descripcion_servicio = models.CharField(max_length=800)
    equipo_complementario = models.CharField(max_length=800, null=True)
    ing_realizo = models.CharField(max_length=100)
    fallo_paciente = models.BooleanField()
    equipo_medico = models.ManyToManyField(Equipo_medico, related_name='equipo_orden')


