# -*- coding: utf-8 -*-
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import os


class GeneratePDFReport:
	def __init__(self, money, quantity,  report_name, product={}):
		self.money = money
		self.quantity = quantity
		self.product_title = product['title']
		self.product_quant = product['quantity']
		self.report_name = report_name

	def create_report(self):
		report_name = "{}/temp/{}.pdf".format(os.getcwd(), self.report_name)
		c = canvas.Canvas(report_name, pagesize=A4)
		width, height = A4
		position_t = 20

		stylesheet = getSampleStyleSheet()
		styleN = stylesheet['Normal']
		styleN.fontSize = 17

		p = Paragraph(u'<para align="center">Last 24h Report</para>', styleN)
		w,h = p.wrap(width, height)
		p.drawOn(c, 0, height-position_t)

		position = 160
		data = []

		data.append(['Most selling product', '', '', '', self.product_title, str(self.product_quant) + ' pcs.'])

		data.append(['Money earned in last 24h', '', '', '', '', self.money])
		data.append(['Quantity of products sold in last 24h', '', '', '', '', self.quantity])
		t=Table(data, [90, 30, 45, 70, 120, 80])
		t.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'RIGHT'),
							('GRID', (0,0), (-1,-1), 0.25, colors.black),
							('ALIGN', (0,-3), (0,-1), 'RIGHT'),
							('SPAN', (0,-1), (-2,-1)),
							('SPAN', (0,-2), (-2,-2)),
							('SPAN', (0, -3), (-3,-3)),
						]))
		w,h = t.wrap(width, height)
		t.drawOn(c, 50, (height-position))

		c.showPage()
		c.save()
