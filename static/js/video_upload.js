// js/video_admin.js
(function ($) {
    $(document).ready(function () {
        // Target the video admin form (adjust selector if needed)
        var $form = $('form[id^="video_form"]');

        if ($form.length) {
            // Add progress bar elements
            var $progressContainer = $('<div>').css({
                'margin': '10px 0',
                'width': '100%',
                'backgroundColor': '#ddd'
            });
            var $progressBar = $('<div>').css({
                'width': '0%',
                'height': '20px',
                'backgroundColor': '#4CAF50',
                'textAlign': 'center',
                'lineHeight': '20px',
                'color': 'white'
            }).text('0%');
            $progressContainer.append($progressBar);
            $form.before($progressContainer);

            // Intercept form submission
            $form.on('submit', function (e) {
                e.preventDefault();
                var formData = new FormData(this);
                var xhr = new XMLHttpRequest();

                xhr.open('POST', this.action, true);
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

                // Track upload progress
                xhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        var percent = Math.round((e.loaded / e.total) * 100);
                        $progressBar.css('width', percent + '%').text(percent + '%');
                    }
                });

                // Handle response
                xhr.onload = function () {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        // Redirect if response is a success
                        window.location.href = xhr.responseURL;
                    } else {
                        // Display form errors
                        document.open();
                        document.write(xhr.responseText);
                        document.close();
                    }
                };

                xhr.send(formData);
            });
        }
    });
})(django.jQuery);