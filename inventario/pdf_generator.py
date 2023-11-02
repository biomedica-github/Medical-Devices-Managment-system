from fpdf import FPDF
from fpdf.fonts import FontFace

import boto3
import os

class PDF(FPDF):
    def header(self):
        # Logo
        self.image("media/IMSS_Logo.png", 10, 8, 25)
        self.set_font("helvetica", "B", 20)
        self.cell(70)
        # Title
        self.cell(55, 25, "IMSS UMAE #2", ln=1, align="C")
        self.set_font("helvetica", "B", 16)
        self.cell(70)
        self.cell(55, 10, "ORDEN DE SERVICIO", ln=1, align="C")
        self.cell(70)
        self.set_font("helvetica", "B", 12)
        self.cell(55, 5, "INGENIERIA BIOMEDICA / CONSERVACION", ln=1, align="C")
        # Line break
        self.ln(10)


def generarOrdenServicio(orden_de_servicio):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", "", 9)
    headings_style = FontFace(emphasis="", color=0, fill_color=(0, 120, 76))

    values = list(orden_de_servicio.values())
    keys = list(orden_de_servicio.keys())

    i = 0

    for value in values:
        if value is None:
            value = "N/A"
        valor = str(value)

        if keys[i] == "fecha_str":
            fecha = valor
        elif keys[i] == "id":
            id = valor
        elif keys[i] == "falla":
            falla = valor
        elif keys[i] == "responsable":
            responsable = valor
        elif keys[i] == "equipo":
            equipo_medico = str(orden_de_servicio["equipo"]["nombre_equipo"])
            marca = str(orden_de_servicio["equipo"]["marca"])
            numero_nacional = str(orden_de_servicio["equipo"]["numero_nacional_inv"])
            modelo = str(orden_de_servicio["equipo"]["nombre_equipo"])
            numero_serie = str(orden_de_servicio["equipo"]["numero_serie"])
            area = str(orden_de_servicio["equipo"]["area"])
            cama = str(orden_de_servicio["equipo"]["cama"])
            if orden_de_servicio["equipo"]["contrato"]:
                contrato = str(orden_de_servicio["equipo"]["contrato"]["tipo_contrato"])
            else:
                contrato = "No tiene contrato"

        elif keys[i] == "descripcion":
            descripcion = valor
        elif keys[i] == "solucion_tecnico":
            solucion_tecnico = valor
        elif keys[i] == 'orden':
            numero_orden= str(orden_de_servicio['orden']['numero_orden'])
        elif keys[i] == 'equipo_complementario':
            equipo_complementario = str(valor)
        elif keys[i] == 'fecha_entrega_str':
            fecha_entrega = str(valor)
        # else:
        #     print(keys[i])

        i += 1

    # numero_orden = orden_de_servicio['numero_orden']
    # fecha = orden_de_servicio['fecha']
    # falla = orden_de_servicio['falla']
    # responsable = orden_de_servicio['responsable']
    # descripcion_servicio = orden_de_servicio['descripcion_servicio']
    # equipo_medico = orden_de_servicio['equipo']['nombre_equipo']

    with pdf.table(
        col_widths=(1, 1, 1, 1, 1),
        headings_style=headings_style,
        line_height=2.5 * pdf.font_size,
    ) as table:
        row = table.row()

        row.cell(
            "DATOS DEL EQUIPO",
            colspan=4,
            align="C",
        )
        row.cell("No. ORDEN", align="C")

        row = table.row()
        row.cell("EQUIPO:")
        row.cell(equipo_medico, colspan=3)
        row.cell(numero_orden, align="C")

        row = table.row()
        row.cell("MARCA:")
        row.cell(marca)
        row.cell("N. DE SERIE:")
        row.cell(numero_serie)
        row.cell("FECHA:", align="C")

        row = table.row()
        row.cell("MODELO:")
        row.cell(modelo)
        row.cell("N. DE INVENTARIO:")
        row.cell(numero_nacional)
        row.cell("Reportado:" + fecha)
        

        row = table.row()
        row.cell("SERVICIO:")
        row.cell("Correctivo")
        row.cell("UBICACION:")
        row.cell(area)
        row.cell("Entrega:"+ fecha_entrega)
    pdf.ln(2)
    with pdf.table(
        col_widths=(1, 1, 1, 1, 1),
        headings_style=headings_style,
        line_height=2.5 * pdf.font_size,
    ) as table:
        row = table.row()

        row.cell(
            "DESCRIPCION DE LA FALLA",
            colspan=4,
            align="C",
        )
        row.cell("SERVICIO", align="C")

        row = table.row()
        row.cell("REPORTADA: " + falla, colspan=4)
        row.cell(contrato, align="C")

        row = table.row()
        row.cell("ENCONTRADA: " + descripcion, colspan=5)
        # row.cell("GARANTIA")

        # row = table.row()
        # row.cell("", colspan=4)
        # row.cell("PROPIO")

        # row = table.row()
        # row.cell("", colspan=4)
        # row.cell("OTRO")

    pdf.ln(2)
    with pdf.table(
        headings_style=headings_style, line_height=2.5 * pdf.font_size
    ) as table:
        row = table.row()

        row.cell("ACTIVIDAD REALIZADA", align="C")

    with pdf.table(line_height=25) as table:
        row = table.row()
        row.cell(solucion_tecnico, align="C")

    pdf.ln(2)
    with pdf.table(
        col_widths=(70, 10),
        headings_style=headings_style,
        line_height=2.5 * pdf.font_size,
    ) as table:
        row = table.row()
        
        row.cell("REFACCIONES O CONSUMIBLES", align='C', colspan=2)
        
       
    with pdf.table(
        line_height=25

        ) as table:
        row = table.row()
        row.cell(equipo_complementario, align="C")

    pdf.ln(2)
    with pdf.table(
        col_widths=(50, 50),
        headings_style=headings_style,
    ) as table:
        row = table.row()

        row.cell("RESPONSABLE DEL SERVICIO", align="C")
        row.cell("NOMBRE Y FIRMA DEL USUARIO", align="C")

    with pdf.table(col_widths=(50, 50), line_height=21) as table:
        row = table.row()
        row.cell("Ramon Ivan Valenzuela Corral", align='C')
        row.cell(responsable, align='C')
   
    with pdf.table(
        col_widths=(50, 50),
    ) as table:
        row = table.row()
        row.cell("BIOMEDICA/CONSERVACION", align='C')
        row.cell(area, align='C')

    # Guardar el PDF

    pdf.output(
        name="static/" + f"OrdenServicio_{id}_{equipo_medico}.pdf"
    )

    s3 = boto3.client('s3')
    with open("static/" + f"OrdenServicio_{id}_{equipo_medico}.pdf", "rb") as f:
        s3.upload_fileobj(f, "bucketeer-74a9acd7-e668-4ac9-9fdd-de748191c984", "Ordenes_servicio/" +f"OrdenServicio_{id}_{equipo_medico}.pdf")

    return f"OrdenServicio_{id}_{equipo_medico}.pdf"
