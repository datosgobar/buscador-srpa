def init_template_filters(app):
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
              'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    @app.template_filter('date_format_ar')
    def date_format_ar(date):
        month = months[date.month - 1]
        return date.strftime('%d de {month} de %Y'.format(month=month))
