document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#SearchCarta').addEventListener('input', () => SubmitValidation());
});

function SubmitValidation() {

    const currentValue = document.getElementById('SearchCarta').value;

    document.getElementById("SearchButton").disabled =
      currentValue.length === 0 ||
      document.querySelector('option[value="' + currentValue + '"]') === null;

}