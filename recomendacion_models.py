from odoo import models, fields, api
from odoo.exceptions import UserError

class RecomendacionRabano(models.Model):
    _name = 'agricultura.recomendacion'
    _description = 'Sistema de recomendaciones para cultivo de rábano'
    
    # --- CAMPOS DE ENTRADA ---
    variedad_rabano_id = fields.Many2one(
        'agricultura.rabano', 
        string='Variedad de Rábano', 
        required=True,
        #domain="[('id', 'in', variedades_disponibles)]")
    )
    
    tipo_suelo = fields.Selection([
        ('arcilloso', 'Arcilloso'),
        ('arenoso', 'Arenoso'),
        ('limoso', 'Limoso'),
        ('franco', 'Franco'),
        ('calcáreo', 'Calcáreo')], 
        string='Tipo de Suelo', 
        required=True)
    
    clima = fields.Selection([
        ('templado', 'Templado (15-20°C)'),
        ('calido', 'Cálido (20-30°C)'),
        ('frio', 'Frío (5-15°C)'),
        ('seco', 'Seco (baja humedad)'),
        ('humedo', 'Húmedo (alta humedad)')], 
        string='Clima Actual', 
        required=True)
    
    tamano_cultivo = fields.Selection([
        ('pequeno', 'Pequeño (Menos de 100 m²)'),
        ('mediano', 'Mediano (100-500 m²)'),
        ('grande', 'Grande (Más de 500 m²)')], 
        string='Tamaño del Cultivo', 
        required=True)
    
    ph_suelo = fields.Float(
        string='pH del Suelo (opcional)',
        help="Si conoce el pH actual de su suelo")
    
    # --- CAMPOS CALCULADOS ---
    porcentaje_exito = fields.Float(
        string='Probabilidad de Éxito (%)', 
        compute='_calcular_porcentaje_exito',
        store=True)
    
    recomendaciones = fields.Text(
        string='Recomendaciones Técnicas', 
        compute='_generar_recomendaciones')
    
    alertas = fields.Text(
        string='Alertas Importantes', 
        compute='_generar_alertas')
    
    # --- MÉTODOS COMPUTADOS ---
    @api.depends('variedad_rabano_id', 'tipo_suelo', 'clima', 'ph_suelo')
    def _calcular_porcentaje_exito(self):
        for rec in self:
            if not rec.variedad_rabano_id:
                rec.porcentaje_exito = 0
                continue
            
            base = 50  # Base inicial ajustable
            
            # 1. Compatibilidad climática (30% peso)
            if rec.clima in rec.variedad_rabano_id.clima_optimo:
                base += 30
            elif ('templado' in rec.variedad_rabano_id.clima_optimo and 
                  rec.clima in ['calido','frio']):
                base += 15
            elif ('frio' in rec.variedad_rabano_id.clima_optimo and 
                  rec.clima == 'calido'):
                base -= 10
            
            # 2. Compatibilidad de suelo (25% peso)
            if rec.tipo_suelo in rec.variedad_rabano_id.suelos_adecuados:
                base += 25
            elif 'franco' in rec.variedad_rabano_id.suelos_adecuados:
                base += 15
            elif 'calcáreo' in rec.tipo_suelo and 'calcáreo' not in rec.variedad_rabano_id.suelos_adecuados:
                base -= 20
            
            # 3. pH del suelo (20% peso)
            if rec.ph_suelo:
                ph_min = rec.variedad_rabano_id.ph_minimo
                ph_max = rec.variedad_rabano_id.ph_maximo
                if ph_min <= rec.ph_suelo <= ph_max:
                    base += 20
                elif (rec.ph_suelo < ph_min) or (rec.ph_suelo > ph_max):
                    base -= 15
            
            # 4. Ajuste por tamaño (5% peso)
            if rec.tamano_cultivo == 'mediano':
                base += 5
            
            rec.porcentaje_exito = max(10, min(100, base))

    def _generar_recomendaciones(self):
        for rec in self:
            if not rec.variedad_rabano_id:
                rec.recomendaciones = "Seleccione una variedad de rábano"
                continue
            
            rabano = rec.variedad_rabano_id
            recoms = [
                f"## Recomendaciones para {rabano.name} ##",
                f"• Profundidad de siembra: {rabano.profundidad_siembra} cm",
                f"• Espaciamiento: {rabano.espacio_plantas} cm entre plantas",
                f"• Riego: {'Frecuente' if rabano.requerimiento_agua == 'alto' else 'Moderado'}"
            ]
            
            # Recomendaciones de suelo
            if rec.tipo_suelo not in rabano.suelos_adecuados:
                if 'franco' in rabano.suelos_adecuados:
                    recoms.append("• ENMIENDA: Añadir 5kg/m² de compost para mejorar estructura")
                if 'calcáreo' in rec.tipo_suelo:
                    recoms.append("• AJUSTE pH: Aplicar azufre si pH > 7.5")
            
            # Recomendaciones de clima
            if rec.clima not in rabano.clima_optimo:
                if 'frio' in rec.clima and 'frio' not in rabano.clima_optimo:
                    recoms.append("• PROTECCIÓN: Usar cubiertas flotantes en noches frías")
                if 'calido' in rec.clima and 'calido' not in rabano.clima_optimo:
                    recoms.append("• SOMBRA: Proporcionar sombra parcial en horas pico")
            
            rec.recomendaciones = "\n".join(recoms)
    
    def _generar_alertas(self):
        for rec in self:
            if not rec.variedad_rabano_id:
                rec.alertas = ""
                continue
            
            alertas = []
            rabano = rec.variedad_rabano_id
            
            # Alertas de pH
            if rec.ph_suelo:
                if rec.ph_suelo < rabano.ph_minimo:
                    alertas.append(f"⚠️ pH BAJO ({rec.ph_suelo}): Aplicar cal para elevar pH a {rabano.ph_minimo}-{rabano.ph_maximo}")
                elif rec.ph_suelo > rabano.ph_maximo:
                    alertas.append(f"⚠️ pH ALTO ({rec.ph_suelo}): Aplicar azufre para reducir pH a {rabano.ph_minimo}-{rabano.ph_maximo}")
            
            # Alertas climáticas
            if ('frio' in rec.clima and 'frio' not in rabano.clima_optimo) or \
               ('calido' in rec.clima and 'calido' not in rabano.clima_optimo):
                alertas.append(f"⚠ CLIMA NO ÓPTIMO: Esta variedad prefiere clima {rabano.clima_optimo}")
            
            # Alertas de suelo
            if rec.tipo_suelo not in rabano.suelos_adecuados:
                alertas.append(f"⚠ SUELO SUBÓPTIMO: Esta variedad crece mejor en {rabano.suelos_adecuados}")
            
            rec.alertas = "\n".join(alertas) if alertas else "✅ Condiciones dentro de parámetros aceptables"
    
    # --- MÉTODOS ADICIONALES ---
    
    @api.model
    def variedades_disponibles(self):
        return self.env['agricultura.rabano'].search([]).ids