module.exports = Marionette.LayoutView.extend({

    template: require('templates/builder/pageDetails/pageElements/types/choicesView'),
    className: 'has-choices select',

    regions: {
        choicesList: 'div.choices-list',
    },

    behaviors: {
        ChoiceBasedElementBehavior: { }
    },

});
