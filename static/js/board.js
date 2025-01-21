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

async function postThread() {
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

        const response = await fetch(`/thread`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        // Assuming the server responds with the thread ID of the newly created thread
        const responseData = await response.json();
        console.log('Response from server:', responseData);

        // Set the hash to the new thread ID
        const newThreadId = responseData.id; // Replace with the actual key from the server response
        window.location.hash = `t${newThreadId}`;

        if(document.getElementById('image-t').files && document.getElementById('image-t').files.length > 0){
            uploadImage(newThreadId, null)    
        }else{
            location.reload()
        }
        

    } catch (error) {
        console.error('Error sending POST request:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash;
    if (hash) {
        const elementId = hash.replace('#', ''); // Remove the hash symbol
        const element = document.getElementById(elementId);
        if (element) {
            // Smoothly scroll to the element
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Clear the hash without modifying the history or reloading the page
            history.replaceState(null, null, ' ');

            // Highlight the post
            highlightPost({ id: elementId });
        } else {
            console.log('Element not found for hash:', hash);
        }
    }
});

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

        const response = await fetch(`/reply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(replyData),
        })

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const responseData = await response.json();

        const newReplyId = responseData.id; // Replace with the actual key from the server response
        window.location.hash = `r${newReplyId}`;

        document.getElementById('reply_content').value = ''

        if(document.getElementById('image-r').files && document.getElementById('image-r').files.length > 0){
            uploadImage(null, newReplyId)    
        }else{
            location.reload()
        }
        

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

const uploadImage = async (thread_id, reply_id) => {
    const fileInput = document.getElementById(thread_id ? 'image-t' : 'image-r');
    const file = fileInput.files[0];
    const threadId = thread_id;
    const replyId = reply_id

    if(thread_id){
        if (!file) {
            console.error("File required");
            return;
        }    
    }
    

    const fileSize = file.size;

    const img = new Image();
    img.src = URL.createObjectURL(file);

    img.onload = async () => {
        const width = img.width;
        const height = img.height;

        const formData = new FormData();
        formData.append('image', file);
        formData.append('name', file.name);
        formData.append('size', fileSize);
        formData.append('measures', `${width}x${height}`);
        formData.append('thread_id', threadId);
        formData.append('reply_id', replyId);

        try {
            const response = await fetch(`/image`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const responseData = await response.json();
                console.log('Image uploaded successfully:', responseData);
                window.location.reload();
            } else {
                const errorData = await response.json();
                console.error('Failed to upload image:', errorData.error || response.statusText);
            }
        } catch (error) {
            console.error('Error uploading image:', error);
        } finally {
            URL.revokeObjectURL(img.src);
        }
    };

    img.onerror = () => {
        console.error('Error loading image to get dimensions');
    };
};



