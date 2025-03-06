# -*- coding: utf-8 -*-
from datetime import timedelta, date
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EjemplarBiblioteca(models.Model):
    _name = 'ejemplar.biblioteca'
    _description = 'Ejemplar para Préstamo'
    _res_name = 'display_name'

    comic_id = fields.Many2one('biblioteca.comic', string='Cómic')
    socio_id = fields.Many2one('socio.biblioteca', string='Socio en Préstamo', ondelete='set null')
    fecha_prestamo = fields.Date('Fecha de Préstamo', default=fields.Date.today)
    fecha_devolucion = fields.Date('Fecha Esperada de Devolución')
    retrasado = fields.Boolean('Entrega Retrasada', compute='_compute_retraso', store=True)
    disponibilidad = fields.Char('Disponible', compute='_compute_disponibilidad', default="Disponible", store=True)
    esta_disponible = fields.Boolean("¿Disponible?", compute="_compute_esta_disponible", store=True)
    portada = fields.Binary(string="Portada Relacionada", related='comic_id.portada', store=False, readonly=True)

    estado_de_conservacion = fields.Selection([
        ('perfecto', 'Como nuevo'),
        ('regular', 'Usado'),
        ('danado', 'Muy usado'),
        ('roto', 'Estropeado')
    ], string='Estado de Conservación', default='perfecto')

    display_name = fields.Char(string='Ejemplar', compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('fecha_prestamo_check', 'CHECK(fecha_prestamo <= CURRENT_DATE)',
         'La fecha de préstamo no puede ser posterior al día de hoy.'),
        ('fecha_devolucion_check', 'CHECK(fecha_devolucion >= CURRENT_DATE)',
         'La fecha prevista de devolución no puede ser anterior al día de hoy.'),
        ('check_fechas', 'CHECK(fecha_prestamo < fecha_devolucion)',
         'La fecha de devolución debe ser posterior a la fecha de préstamo.')
    ]

    def name_get(self):
        """Modifica cómo se representa el cómic tomado en préstamo"""
        result = []
        for record in self:
            estado = dict(self._fields['estado_de_conservacion'].selection).get(record.estado_de_conservacion,
                                                                                "Desconocido")
            result.append(
                (record.id, f"{record.comic_id.name} ({estado})" if record.comic_id else "Sin cómic asociado"))
        return result

    @api.depends('fecha_devolucion')
    def _compute_retraso(self):
        """Calcula si el ejemplar está retrasado basado en la fecha de devolución esperada."""
        hoy = fields.Date.today()
        for record in self:
            record.retrasado = record.fecha_devolucion and record.fecha_devolucion < hoy

    @api.depends("socio_id")
    def _compute_esta_disponible(self):
        """Determina si el ejemplar está disponible para préstamo."""
        for record in self:
            record.esta_disponible = not record.socio_id

    @api.onchange('socio_id')
    def _delete_if_no_user(self):
        """Operación si se borra el socio del ejemplar."""
        for record in self:
            if not record.socio_id:
                record.esta_disponible = True
                record.fecha_devolucion = False
                record.fecha_prestamo = False
                record.disponibilidad = "Disponible"

    @api.depends('socio_id', 'retrasado', 'fecha_devolucion')
    def _compute_disponibilidad(self):
        """Cálculo del estado de disponibilidad como cadena."""
        for record in self:
            if not record.socio_id:
                record.disponibilidad = "Disponible"
            elif record.retrasado:
                record.disponibilidad = "Devolución retrasada"
            else:
                record.disponibilidad = str(record.fecha_devolucion)

    @api.depends('comic_id', 'estado_de_conservacion')
    def _compute_display_name(self):
        """Calcula el nombre basado en el `name_get`."""
        for record in self:
            estado = dict(self._fields['estado_de_conservacion'].selection).get(record.estado_de_conservacion,
                                                                                "Desconocido")
            record.display_name = f"{record.comic_id.name} ({estado})" if record.comic_id else "Sin cómic asociado"

    @api.model
    def obtener_ejemplares_disponibles(self):
        """Obtiene una lista de ejemplares disponibles."""
        return self.search([('esta_disponible', '=', True)])

    def _prestamo_comprobaciones(self, socio_id, ejemplar_id):
        """Verifica las condiciones para un préstamo."""
        if not socio_id or not ejemplar_id:
            raise ValidationError("No se pudo determinar el socio o el ejemplar.")
        socio = self.env['socio.biblioteca'].browse(socio_id)
        ejemplar = self.env['ejemplar.biblioteca'].browse(ejemplar_id)

        if not socio.exists() or not ejemplar.exists():
            raise ValidationError(f"No se encontró el Socio {socio} o el Ejemplar {ejemplar_id} en el sistema.")

        if not ejemplar.esta_disponible:
            raise ValidationError(f"El ejemplar '{ejemplar.display_name}' no está disponible.")

        return socio, ejemplar

    def action_prestar_individual(self):
        """Acción para prestar un ejemplar al socio actualmente visualizado."""
        socio_id = self.env.context.get('socio_biblioteca_id')
        ejemplar_id = self.env.context.get('ejemplar_id')

        socio, ejemplar = self._prestamo_comprobaciones(socio_id, ejemplar_id)

        ejemplar.write({
            'socio_id': socio.id,
            'esta_disponible': False,
            'fecha_prestamo': fields.Date.context_today(self),
            'fecha_devolucion': fields.Date.context_today(self) + timedelta(days=15),
        })

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_devolver_individual(self):
        """Acción para devolver un ejemplar individual."""
        for record in self:
            if record.esta_disponible:
                raise ValidationError("El ejemplar ya está disponible. No se puede devolver.")

            record.esta_disponible = True
            record.socio_id = False
            record.fecha_devolucion = fields.Date.context_today(self)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Devolución Exitosa',
                    'message': f'El ejemplar "{record.display_name}" ha sido devuelto.',
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                },
            }
