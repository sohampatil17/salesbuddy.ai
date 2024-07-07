$(document).ready(function() {
    $('#output').hide();
    $('#company-table').DataTable();

    $('#input-form').submit(function(e) {
        e.preventDefault();
        
        const inputPrompt = $('#input_prompt').val();

        $.post('/get_companies', { input_prompt: inputPrompt }, function(data) {
            console.log("Response Data:", data);  // Debugging line
            const outputBody = $('#output-body');
            outputBody.empty();

            data.forEach(company => {
                const row = `<tr>
                    <td>${company.name}</td>
                    <td><a href="${company.linkedin}" target="_blank">${company.linkedin}</a></td>
                    <td>${company.size}</td>
                    <td>${company.funding}</td>
                    <td>${company.year_founded}</td>
                    <td>${company.head_office_location}</td>
                    <td>Email: ${company.sales_contact.email}<br>Phone: ${company.sales_contact.phone}</td>
                </tr>`;
                outputBody.append(row);
            });

            $('#output').show();
            $('#company-table').DataTable().draw();
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.log("Request Failed:", textStatus, errorThrown);  // Debugging line
        });
    });
});
