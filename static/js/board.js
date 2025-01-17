const getFingerprint = async () => {
    const storedFingerprint = localStorage.getItem('fingerprint');
    if (storedFingerprint) {
        return storedFingerprint; // Reuse the stored fingerprint
    }

    try {
        const fp = await FingerprintJS.load();
        const result = await fp.get();
        console.log('Generated fingerprint:', result.visitorId);

        // Save fingerprint to localStorage for reuse
        localStorage.setItem('fingerprint', result.visitorId);

        return result.visitorId;
    } catch (error) {
        console.error('Error generating fingerprint:', error);
        throw error;
    }
};


async function sendPostRequest() {
    try {
        const token = await getFingerprint();
        console.log('User Token:', token);

        const titleInput = document.getElementById('title');
        const contentInput = document.getElementById('content');
        const boardIdInput = document.getElementById('board_id');

        const title = titleInput ? titleInput.value.trim() : '';
        const content = contentInput ? contentInput.value.trim() : '';
        const board_id = boardIdInput ? boardIdInput.value.trim() : '';

        if (!title || !content || !board_id) {
            console.error('Title, content, or board ID is missing.');
            return;
        }

        // Clear input fields after extracting their values
        if (titleInput) titleInput.value = '';
        if (contentInput) contentInput.value = '';

        const currentDateTime = new Date();
        const year = currentDateTime.getUTCFullYear();
        const month = String(currentDateTime.getUTCMonth() + 1).padStart(2, '0');
        const day = String(currentDateTime.getUTCDate()).padStart(2, '0');
        const date = `${year}-${month}-${day}`;

        const hours = String(currentDateTime.getUTCHours()).padStart(2, '0');
        const minutes = String(currentDateTime.getUTCMinutes()).padStart(2, '0');
        const seconds = String(currentDateTime.getUTCSeconds()).padStart(2, '0');
        const time = `${hours}:${minutes}:${seconds}`;

        const postData = {
            user_token: token,
            title: title,
            content: content,
            board_id: board_id,
            date: date,
            time: time,
            type: 0,
        };

        console.log('Post data:', postData);

        const response = await fetch('http://127.0.0.1:5000/thread', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const responseData = await response.json();
        console.log('Response from server:', responseData);
    } catch (error) {
        console.error('Error sending POST request:', error);
    }
}
