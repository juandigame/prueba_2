from odoo import models, fields, api

class Rabano(models.Model):
    _name = 'agricultura.rabano'
    _description = 'Información técnica sobre variedades de rábano'
    
    name = fields.Char(
        string='Variedad de Rábano', 
        required=True,
        help="Ejemplo: Cherry Belle, Daikon, French Breakfast")
    
    descripcion = fields.Text(
        string='Características', 
        help="Descripción detallada de la variedad")
    
    dias_cosecha = fields.Integer(
        string='Días hasta cosecha', 
        required=True,
        help="Rango promedio desde siembra hasta cosecha")
    
    imagen = fields.Binary(string='Imagen de referencia')
    
    # --- NUEVOS CAMPOS TÉCNICOS ---
    clima_optimo = fields.Selection([
        ('templado', 'Templado (15-20°C)'),
        ('calido', 'Cálido (20-30°C)'),
        ('frio', 'Frío (5-15°C)')],
        string='Clima Óptimo', 
        required=True,
        default='templado')
    
    ph_minimo = fields.Float(
        string='pH Mínimo', 
        default=6.0,
        help="pH mínimo del suelo tolerable")
    
    ph_maximo = fields.Float(
        string='pH Máximo', 
        default=7.0,
        help="pH máximo del suelo tolerable")
    
    profundidad_siembra = fields.Float(
        string='Profundidad de siembra (cm)',
        default=1.5,
        help="Profundidad recomendada para sembrar")
    
    espacio_plantas = fields.Float(
        string='Espacio entre plantas (cm)',
        default=5.0,
        help="Distancia recomendada entre plantas")
    
    suelos_adecuados = fields.Selection([
        ('arcilloso', 'Arcilloso (con enmiendas)'),
        ('arenoso', 'Arenoso (ideal con compost)'),
        ('limoso', 'Limoso'),
        ('franco', 'Franco (óptimo)'),
        ('calcáreo', 'Calcáreo (requiere ajuste pH)')],
        string='Suelos Adecuados', 
        required=True,
        default='franco')
    
    requerimiento_agua = fields.Selection([
        ('alto', 'Alto (riego frecuente)'),
        ('medio', 'Moderado (3-4 veces/semana)'),
        ('bajo', 'Bajo (tolerante a sequía)')],
        string='Necesidad hídrica',
        default='medio')
    
    resistencia_enfermedades = fields.Text(
        string='Resistencias conocidas',
        help="Ejemplo: Resistente a fusarium, mildiu, etc.")
    
    notas_especiales = fields.Text(
        string='Recomendaciones especiales',
        help="Cuidados específicos para esta variedad")
    
    def action_abrir_recomendacion(self):
        """Método para abrir el asistente de recomendaciones desde el formulario de variedad"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar Recomendación',
            'res_model': 'agricultura.recomendacion',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_variedad_rabano_id': self.id
            }
        }