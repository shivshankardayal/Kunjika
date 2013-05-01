$('#register').validate({
    rules: {
        name: {
            minlength: 2,
            required: true
        },
        lname: {
            minlength: 2,
            required: true
        },
        username: {
            minlength: 2,
            required: true,
            remote: {
                url: '/verify_username',
                cache: false
            }
        },
        email: {
            required: true,
            email: true,
            remote: {
                url: '/verify_email',
                cache: false
            }
        },
        password: {
            required: true,
            minlength: 8,
            maxlength: 250
        },
        password2: {
            equalTo: '#password'
        },
        postal_code: {
            required: true,
            minlength: 5
        }
    },
    messages: {
        name: "Please enter your first name",
        lname: "Please enter your last name",
        username: {
            required: "Please enter a username",
            minlength: "Your username must consist of at least {0} characters"
        },
        email: "Please enter a valid email address",
        password: {
            required: "Please provide a password",
            minlength: "Your password must be at least {0} characters long",
            maxlength: "Your password must be less than {0} characters long"
        },
        password2: {
            equalTo: "Please enter the same passwords"
        },
        postal_code: "Please enter a valid zip code"
    },
    highlight: function (element, errorClass, validClass) {
        $(element).closest('.control-group').removeClass('success').addClass('error');
    },
    unhighlight: function (element, errorClass, validClass) {
        $(element).closest('.control-group').removeClass('error').addClass('success');
    },
    success: function (label) {
        $(label).closest('form').find('.valid').removeClass("invalid");
    },
    errorPlacement: function (error, element) {
        element.closest('.control-group').find('.help-block').html(error.text());
    }
});