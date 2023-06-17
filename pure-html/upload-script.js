const fileUploadBtn = document.getElementById('fileUploadBtn');
const fileInput = document.getElementById('fileInput');

fileUploadBtn.addEventListener('click', handleFileUpload);

function handleFileUpload() {
    fileInput.click();
}

fileInput.addEventListener('change', handleFilesSelected);

function handleFilesSelected(event) {
    const files = event.target.files;
    // Process the selected files here
    console.log(files);
}
