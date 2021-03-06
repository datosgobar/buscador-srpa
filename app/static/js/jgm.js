window.jgm = window.jgm || {};
window.jgm.results = {
    highlight: function (questionId, words) {
        var question = $('.result[data-question-id=' + questionId + ']');
        var options = {
            accuracy: {
                value: 'exactly',
                limiters: [
                    '¡', '!', '@', '#', '&', '*', '(', ')', '-', '–', '—', '+',
                    '=', '[', ']', '{', '}', '|', ':', ';', '\'', '\"', '‘',
                    '’', '“', '”', ',', '.', '<', '>', '/', '¿', '?'
                ]
            }
        };
        question.find('p.question-body').mark(words, options);
        question.find('p.question-context').mark(words, options);
        question.find('p.question-answer').mark(words, options);
    }
};

$(function () {
    $(document).ajaxStart(NProgress.start);
    $(document).ajaxStop(NProgress.done);
    $(window).on('beforeunload', function() {
        NProgress.start();
        return undefined;
    })
});

