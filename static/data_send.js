
const sendToFlask = (data) => {
    $.ajax({
        url: "/process",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ "data": data }),
        success: function(response) {
            console.log(response);
        },
        error: console.log,
    });
};

