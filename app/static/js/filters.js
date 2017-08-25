$(function() {
    var searchFilters = $('#search-filters');

    searchFilters.find('.add-filter').on('click', function() {
        searchFilters.find('.add-filter-container').addClass('hidden');
        $('#filter-picker').removeClass('hidden');
    });
    searchFilters.find('.cancel-filter').on('click', function() {
        searchFilters.find('.add-filter-container').removeClass('hidden');
        $('#filter-picker').addClass('hidden');
    });
    var showValuePicker = function() {
        var behaviourSelected = searchFilters.find('#filter-behaviour option:selected').val();
        var optionSelected = searchFilters.find('#filter-type option:selected').val();
        searchFilters.find('.filter-value').addClass('hidden').removeClass('active');

        if (behaviourSelected == 'has-value') {
            searchFilters.find('.filter-value[data-filter-type="' + optionSelected + '"]').removeClass('hidden').addClass('active');
            searchFilters.find('#date-filter-comparision-container').toggleClass('hidden', optionSelected != 'date');
            searchFilters.find('#filter-comparision-container').toggleClass('hidden', optionSelected == 'date');
        } else if (behaviourSelected == 'without-value') {
            searchFilters.find('#filter-comparision-container').addClass('hidden');
            searchFilters.find('#date-filter-comparision-container').addClass('hidden');
            searchFilters.find('.filter-value').addClass('hidden');
        }
    };

    var urlConstructor = function (args) {
        var getArgs = [];
        for (var key in args) {
            if (args[key].length > 0) {
                getArgs.push(encodeURIComponent(key) + '=' + encodeURIComponent(args[key]));
            }
        }
        return '/buscar?' + getArgs.join('&');
    };

    var currentArgs = function () {
        var args = jQuery.extend({}, window.jgm.query.filters, {'buscar-usando': window.jgm.query.based_on, 'buscar-dentro-de': window.jgm.query.target});
        if (window.jgm.query.text) {
            args['q'] = window.jgm.query.text;
        }
        return args;
    };

    var updateRemoveLinks = function () {
        var links = $('a.filter-link[data-filter-link-type="remove"]');
        for (var i=0; i<links.length; i++) {
            var link = $(links[i]);
            var newArgs = currentArgs();
            delete newArgs[link.data('filter-name')];
            delete newArgs[link.data('filter-name') + '-comparacion'];
            var newHref = urlConstructor(newArgs);
            link.attr('href', newHref);
        }
    };

    var updateAddLink = function () {
        var selectedBehaviour = searchFilters.find('#filter-behaviour option:selected').val();
        var selectedFilterName = searchFilters.find('#filter-type option:selected').val();
        var newArgs = currentArgs();
        var translations = {
            'informe': 'informe', 'autor': 'autor', 'date': 'fecha',
            'ministerio': 'ministerio', 'área de gestión': 'area'
        };

        if (selectedBehaviour == 'has-value') {
            var selectedComparision;
            if (selectedFilterName == 'date') {
                newArgs[translations[selectedFilterName]] = datePicker.toString('YYYY-MM-DD');
                selectedComparision = searchFilters.find('#date-filter-comparision').val();
            } else {
                newArgs[translations[selectedFilterName]] = searchFilters.find('.filter-value.active option:selected').val();
                selectedComparision = searchFilters.find('#filter-comparision option:selected').val();
            }
            var comparisionTranslation = {
                'different-to': 'diferencia',
                'equal-to': 'igualdad',
                'greater-than': 'mayorigual',
                'less-than': 'menorigual'
            };
            newArgs[translations[selectedFilterName] + '-comparacion'] = comparisionTranslation[selectedComparision];
        } else {
            newArgs[translations[selectedFilterName]] = '';
        }

        
        var link = searchFilters.find('#apply-filter');
        var newHref = urlConstructor(newArgs);
        link.attr('href', newHref);
    };

    searchFilters.find('#filter-behaviour').select2({
        minimumResultsForSearch: Infinity
    });
    searchFilters.find('#filter-comparision').select2({
        minimumResultsForSearch: Infinity
    });
    searchFilters.find('#date-filter-comparision').select2({
        minimumResultsForSearch: Infinity
    });
    searchFilters.find('#filter-type').select2({
        minimumResultsForSearch: Infinity
    });
    searchFilters.find('.filter-value-picker').select2();
    moment.locale("es");
    var datePickerInput = $('#date-filter-value');
    var datePicker = new Pikaday({
        field: datePickerInput[0],
        format: 'D MMM YYYY',
        i18n: {
            previousMonth : 'Mes siguiente',
            nextMonth     : 'Mes anterior',
            months        : ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
            weekdays      : ['Domingo','Lunes','Martes','Miercoles','Jueves','Viernes','Sabado'],
            weekdaysShort : ['Dom','Lun','Mar','Mie','Jue','Vie','Sab']
        }
    })

    var updateFilters = function () {
        showValuePicker();
        updateAddLink();
    };
    searchFilters.on('select2:select', updateFilters);
    datePickerInput.on('change', updateFilters);

    showValuePicker();
    updateRemoveLinks();
    updateAddLink();
});