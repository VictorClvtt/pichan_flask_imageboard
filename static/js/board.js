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


async function sendPostRequest(){
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

        
        
    } catch (error) {
        console.error('Error sending POST request:', error);
    }
}

function replyModal(id){
    document.getElementById('thread_or_reply_id').value = id

    console.log(document.getElementById('thread_or_reply_id').value)
}

async function postReply(){
    try {
        const token = await getFingerprint();
        console.log('User Token:', token);

        const contentInput = document.getElementById('reply_content').value;
        const threadOrReplyIdInput = document.getElementById('thread_or_reply_id').value;

        const content = contentInput ? contentInput.trim() : '';
        const thread_or_reply_id = threadOrReplyIdInput ? threadOrReplyIdInput.trim() : '';

        // Initialize variables to ensure they are available outside the conditionals
        let thread_id = '';
        let reply_id = '';

        // Checking if it's a reply to a thread or a reply
        if (thread_or_reply_id[0] === 't') {
            thread_id = thread_or_reply_id.slice(1);
            console.log('Thread ID:', thread_id);
        } else if (thread_or_reply_id[0] === 'r') {
            reply_id = thread_or_reply_id.slice(1);
            console.log('Reply ID:', reply_id);
        }

        if (!content || !thread_or_reply_id) {
            console.error('Content or thread/reply ID is missing.');
            return;
        }

        // Clear input fields after extracting their values
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

        const replyData = {
            user_token: token,
            content: content,
            date: date,
            time: time,
            thread_id: thread_id,
            reply_id: reply_id
        };

        console.log('Reply data:', replyData);

        const response = await fetch('http://127.0.0.1:5000/reply', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(replyData),
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

function highlightPost(id) {
    var element = document.getElementById(id.id);
    if (element) {
        // Store the original background color
        var originalColor = element.style.backgroundColor;
        
        // Add CSS transition for smooth background color change
        element.style.transition = "background-color 0.5s ease-in-out"; // Change over 0.5 seconds
        
        // Set the background color to a lighter shade
        element.style.backgroundColor = '#00ffd963';

        // After the animation, reset the background color to the original color
        setTimeout(function() {
            element.style.backgroundColor = originalColor;
        }, 400); // Reset after 500 milliseconds (matching the animation duration)
    } else {
        console.log('Element not found with id:', id);
    }
}


