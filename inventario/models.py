from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return self.nombre_proveedor

    class Meta:
        ordering = ["nombre_proveedor"]


class Contrato(models.Model):
    CONTRATO_CONSOLIDADO = "C"
    CONTRATO_GARANTIA = "G"
    CONTRATO_LOCAL = "L"
    CONTRATO_OPCIONES = [
        (CONTRATO_LOCAL, "Contrato local"),
        (CONTRATO_GARANTIA, "Contrato garantia"),
        (CONTRATO_CONSOLIDADO, "Contrato consolidado"),
    ]
    SERVICIO_PREVENTIVO = "PRV"
    SERVICIO_PREV_CORR = "P/C"
    NO_SERVICIO = "N/A"
    SERVICIO_OPCIONES = [
        (SERVICIO_PREV_CORR, "Servicio preventivo y correctivo"),
        (SERVICIO_PREVENTIVO, "Servicio  preventivo"),
        (NO_SERVICIO, "Proveedor no brinda servicio"),
    ]

    num_contrato = models.CharField(max_length=100, unique=True)
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.CASCADE, related_name="proveedor_contrato"
    )
    tipo_contrato = models.CharField(
        max_length=1, choices=CONTRATO_OPCIONES, default=CONTRATO_LOCAL, null=True
    )
    tipo_servicio_estipulado = models.CharField(
        max_length=3, choices=SERVICIO_OPCIONES, default=SERVICIO_PREVENTIVO
    )
    fecha_vencimiento = models.DateField(auto_now=False, auto_now_add=False)
    num_servicios = models.PositiveIntegerField(null=True)

    def __str__(self) -> str:
        return self.num_contrato

    class Meta:
        ordering = ["proveedor"]


class Area_hospital(models.Model):
    nombre_sala = models.CharField(max_length=100)
    responsable = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="responsable_area"
    )

    def __str__(self) -> str:
        return self.nombre_sala

    class Meta:
        ordering = ["nombre_sala"]


class Equipo_medico(models.Model):
    ESTADO_FUNCIONAL = "FUNC"
    ESTADO_FUERA_SERVICIO = "OUT"
    ESTADO_SERVICIO = "SERV"
    ESTADO_BAJA = "BAJA"
    ESTADO_OPCIONES = [
        (ESTADO_FUNCIONAL, "Equipo funcional"),
        (ESTADO_FUERA_SERVICIO, "Equipo fuera de servicio"),
        (ESTADO_SERVICIO, "Equipo en mantenimiento"),
        (ESTADO_BAJA, "Equipo en proceso de baja")
    ]

    numero_nacional_inv = models.CharField(max_length=100, unique=True)
    nombre_equipo = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=4, choices=ESTADO_OPCIONES, default=ESTADO_FUNCIONAL
    )
    observaciones = models.CharField(max_length=255, null=True)
    numero_serie = models.CharField(max_length=255, null=True)
    marca = models.CharField(max_length=50, null=True)
    modelo = models.CharField(max_length=50, null=True)
    contrato = models.ForeignKey(
        Contrato, on_delete=models.SET_NULL, null=True, related_name="equipos_contrato"
    )
    area = models.ForeignKey(
        Area_hospital, on_delete=models.SET_NULL, null=True, related_name="equipos_area"
    )
    cama = models.PositiveIntegerField(null=True)
    carta_obsolescencia_tercero = models.FileField(null=True, upload_to="Anexos")
    dictamen_tecnico_propio = models.FileField(null=True, upload_to="Anexos")
    minuta_baja = models.FileField(null=True, upload_to="Anexos")


    class Meta:
        ordering = ["nombre_equipo"]

    def __str__(self) -> str:
        return f"NNI: {self.numero_nacional_inv} || Nombre: {self.nombre_equipo} || Numero de serie: {self.numero_serie}"




class Orden_Servicio(models.Model):
    MOTIVO_CORRECTIVO = "C"
    MOTIVO_PREVENTIVO = "P"
    MOTIVO_REFACCION = "R"
    MOTIVO_DIAGNOSTICO = "D"
    MOTIVO_OPCIONES = [
        (MOTIVO_CORRECTIVO, "Correctivo"),
        (MOTIVO_PREVENTIVO, "Preventivo"),
        (MOTIVO_DIAGNOSTICO, "Diagnostico"),
        (MOTIVO_REFACCION, "Refaccion"),
    ]

    TIPO_AGENDADA = "A"
    TIPO_ESPONTANEA = "E"
    TIPO_BITACORA = "B"
    TIPO_OPCIONES = [
        (TIPO_AGENDADA, "Orden agendada"),
        (TIPO_ESPONTANEA, "Orden espontanea"),
        (TIPO_BITACORA, "Bitacora"),
    ]

    ESTATUS_FUERA = "OUT"
    ESTATUS_FUNCIONAL = "FUN"
    ESTATUS_NO_SERVICIO = "N/A"
    ESTATUS_PENDIENTE = "PEN"
    ESTATUS_OPCIONES = [
        (ESTATUS_FUNCIONAL, "Equipo funcional"),
        (ESTATUS_FUERA, "Equipo fuera de servicio"),
        (ESTATUS_NO_SERVICIO, "No se realizo servicio"),
        (ESTATUS_PENDIENTE, "Pendiente"),
    ]

    numero_orden = models.CharField(max_length=255, null=True, unique=True)
    fecha = models.DateField(auto_now_add=False, auto_now=False)
    motivo = models.CharField(
        max_length=1, choices=MOTIVO_OPCIONES, default=MOTIVO_PREVENTIVO
    )
    tipo_orden = models.CharField(
        max_length=1, choices=TIPO_OPCIONES, default=TIPO_AGENDADA
    )
    estatus = models.CharField(
        max_length=3, choices=ESTATUS_OPCIONES, default=ESTATUS_PENDIENTE
    )
    responsable = models.CharField(max_length=100, null=True)
    autorizo_jefe_biomedica = models.BooleanField(default=False)
    autorizo_jefe_conservacion = models.BooleanField(default=False)
    descripcion_servicio = models.CharField(max_length=2000, null=True)
    equipo_complementario = models.CharField(max_length=200, null=True)
    ing_realizo = models.CharField(max_length=100, null=True)
    num_mantenimiento_preventivo = models.PositiveSmallIntegerField(null=True)
    fallo_paciente = models.BooleanField(null=True)
    equipo_medico = models.ManyToManyField(Equipo_medico, related_name="equipo_orden")
    contrato = models.ForeignKey(
        Contrato, related_name="contrato_orden", null=True, on_delete=models.SET_NULL
    )
    orden_escaneada = models.FileField(null=True, upload_to="Ordenes_servicio")

    class Meta:
        ordering = ["-fecha"]


class ReporteUsuario(models.Model):
    ESTADO_PENDIENTE = "PEN"
    ESTADO_COMPLETADO = "COM"
    ESTADO_OPCIONES = [(ESTADO_PENDIENTE, "Pendiente"), (ESTADO_COMPLETADO, "Atendido")]

    FALLA_NO_ENCIENDE = "NO/ENC"
    FALLA_ALARMA = "ALARMA"
    FALLA_SENSOR = "SENSOR"
    FALLA_NO_TRABAJA = "NO/TRB"
    FALLA_NO_PASA_PRUEBA = "NO/PRU"
    FALLA_PAPEL = "PAPEL"
    FALLA_OPCIONES = [
        (FALLA_NO_ENCIENDE, "El equipo no enciende"),
        (FALLA_ALARMA, "El equipo marca error o alguna alarma"),
        (
            FALLA_SENSOR,
            "Un sensor esta fallando(Brazalette de PANI, sensor de SPO2, Sensores ECG, etc.)",
        ),
        (
            FALLA_NO_TRABAJA,
            "El equipo no trabaja de forma que deberia(No funcionan perillas, botones, pantalla tactil, etc.)",
        ),
        (FALLA_PAPEL, "Hace falta papel"),
    ]
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name="responsable_reporte",
    )
    estado = models.CharField(
        max_length=3, choices=ESTADO_OPCIONES, default=ESTADO_PENDIENTE
    )
    correo = models.EmailField(null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    area = models.ForeignKey(
        Area_hospital, on_delete=models.SET_NULL, related_name="area_reporte", null=True
    )
    equipo = models.ForeignKey(
        Equipo_medico, on_delete=models.CASCADE, related_name="equipo_reporte"
    )
    falla = models.CharField(max_length=6, choices=FALLA_OPCIONES)
    descripcion = models.CharField(max_length=500, null=True)
    solucion_tecnico = models.CharField(max_length=500, null=True)
    orden = models.ForeignKey(Orden_Servicio, on_delete=models.SET_NULL, null=True)
    equipo_complementario = models.CharField(max_length=500, null=True)

    class Meta:
        ordering = ["-fecha_hora"]


class Evento(models.Model):
    TIPO_VENC_CONTRATO = "CONTR"
    TIPO_SERVICIO = "SERVC"
    TIPO_CAPACITACION = "CAPAC"
    TIPO_CHECKLIST = "CHECK"
    TIPO_OPCIONES = [
        (TIPO_VENC_CONTRATO, "Vencimiento de contrato"),
        (TIPO_SERVICIO, "Servicio preventivo agendado"),
        (TIPO_CAPACITACION, "Curso de capacitacion agendada"),
        (TIPO_CHECKLIST, "Chequeo al equipo agendado"),
    ]
    fecha = models.DateField(auto_now=False, auto_now_add=False)
    tipo_evento = models.CharField(max_length=5, choices=TIPO_OPCIONES)
    contrato = models.OneToOneField(Contrato, on_delete=models.CASCADE, null=True)
    equipo_medico = models.ForeignKey(
        Equipo_medico, on_delete=models.CASCADE, related_name="Evento_equipo", null=True
    )

    class Meta:
        ordering = ["fecha"]


class CheckList(models.Model):
    CONDICION_BUENA = "B"
    CONDICION_MALA = "M"
    CONDICION_NA = "N"
    CONDICION_OPCIONES = [
        (CONDICION_BUENA, "Buena"),
        (CONDICION_MALA, "Mala"),
        (CONDICION_NA, "N/A"),
    ]
    PRUEBA_PASO = "P"
    PRUEBA_NOPASO = "N"
    PRUEBA_OPCIONES = [
        (PRUEBA_PASO, "El equipo paso la prueba de funcionamiento correctamente"),
        (PRUEBA_NOPASO, "El equipo no paso prueba de funcionamiento"),
    ]
    CALIF_1 = 1
    CALIF_2 = 2
    CALIF_3 = 3
    CALIF_4 = 4
    CALIF_5 = 5
    CALIF_OPCIONES = [
        (CALIF_1, "1"),
        (CALIF_2, "2"),
        (CALIF_3, "3"),
        (CALIF_4, "4"),
        (CALIF_5, "5"),
    ]
    fecha_hora = models.DateTimeField(auto_now_add=True)
    area = models.ForeignKey(
        Area_hospital,
        on_delete=models.SET_NULL,
        null=True,
        related_name="area_checklist",
    )
    equipo = models.ForeignKey(
        Equipo_medico, on_delete=models.CASCADE, related_name="equipo_checklist"
    )
    bateria = models.CharField(max_length=1, choices=CONDICION_OPCIONES)
    condicion_general = models.CharField(max_length=1, choices=CONDICION_OPCIONES)
    enciende = models.BooleanField()
    prueba_funcionamiento = models.CharField(max_length=1, choices=PRUEBA_OPCIONES)
    sensor_SPO2 = models.CharField(
        max_length=1, choices=CONDICION_OPCIONES, default=CONDICION_NA
    )
    sensor_TEMP = models.CharField(
        max_length=1, choices=CONDICION_OPCIONES, default=CONDICION_NA
    )
    PANI = models.CharField(
        max_length=1, choices=CONDICION_OPCIONES, default=CONDICION_NA
    )
    sensor_ECG = models.CharField(
        max_length=1, choices=CONDICION_OPCIONES, default=CONDICION_NA
    )
    sensor_PAI = models.CharField(
        max_length=1, choices=CONDICION_OPCIONES, default=CONDICION_NA
    )
    observaciones = models.CharField(max_length=800, null=True)
    desempeño_general = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5)], choices=CALIF_OPCIONES
    )

    class Meta:
        ordering = ["-fecha_hora"]
