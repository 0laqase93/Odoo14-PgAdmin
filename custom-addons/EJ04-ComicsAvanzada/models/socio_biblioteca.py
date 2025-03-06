# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class SocioBiblioteca(models.Model):
    _name = 'socio.biblioteca'
    _description = 'Socio Biblioteca'
    _order = 'nombre'
    _rec_name = 'nombre'
    nombre = fields.Char('Nombre', required=True)
    identificador = fields.Char('Identificador')
    apellido = fields.Char('Apellido')

    ejemplar_ids = fields.One2many(
        'ejemplar.biblioteca',
        'socio_id',
        string='Ejemplares en Préstamo'
    )

    @api.depends('ejemplar_ids')
    def _compute_ejemplares_disponibles(self):
        for socio in self:
            # Buscar todos los ejemplares disponibles
            ejemplares_disponibles = self.env['ejemplar.biblioteca'].search([('esta_disponible', '=', True)])
            socio.ejemplar_disponibles_ids = ejemplares_disponibles

    ejemplar_disponibles_ids = fields.One2many(
        comodel_name='ejemplar.biblioteca',
        compute='_compute_ejemplares_disponibles',
        string="Ejemplares Disponibles"
    )







