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

class Fecha_servicio(models.Model):
    ESTADO_PENDIENTE = 'P'
    ESTADO_REALIZADA = 'R'
    ESTADO_OPCIONES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_REALIZADA, 'Realizada')
    ]
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    equipo_medico = models.ForeignKey(Equipo_medico, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now=False, auto_now_add=False)
    estado = models.CharField(max_length=1, choices=ESTADO_OPCIONES, default=ESTADO_PENDIENTE)

class Orden_Servicio(models.Model):
    MOTIVO_CORRECTIVO = 'C'
    MOTIVO_PREVENTIVO = 'P'
    MOTIVO_AGENDADO = 'A'
    MOTIVO_REFACCION = 'R'
    MOTIVO_DIAGNOSTICO = 'D'
    MOTIVO_OPCIONES = [
        (MOTIVO_AGENDADO, 'Agendado'),
        (MOTIVO_CORRECTIVO, 'Correctivo'),
        (MOTIVO_PREVENTIVO, 'Preventivo'),
        (MOTIVO_DIAGNOSTICO, 'Diagnostico'),
        (MOTIVO_REFACCION, 'Refaccion')
    ]
    
    numero_orden = models.CharField(max_length=100, primary_key=True)
    fecha = models.DateField(auto_now_add=False, auto_now=False)
    estatus = models.CharField(max_length=1, choices=MOTIVO_OPCIONES, )