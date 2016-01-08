module.exports = Marionette.ItemView.extend({

    template: require('templates/procedures/proceduresItemView'),
    tagName: 'li',
    className: 'procedure',

    events: {
        'click a.download': '_onDownloadProcedure',
        'click a.delete': '_onDeleteProcedure',
    },

    onRender: function() {
        this.$el.hide().fadeIn();
    },

    _onDownloadProcedure: function(event) {
        event.preventDefault();
        // TODO
    },

    _onDeleteProcedure: function(event) {
        event.preventDefault();

        // TODO prompt user for confirmation

        let self = this;
        let el = this.$el;

        el.fadeOut(function() {
            self.model.destroy({
                success: function(model, response, options) {
                    console.info('Deleted Procedure', self.model.get('id'));
                },
                error: function(model, response, options) {
                    console.warn('Failed to delete Procedure', self.model.get('id'), response.responseJSON);
                    el.fadeIn();
                    // TODO show error alert
                },
            });
        });
    },

});