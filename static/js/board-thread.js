const getFingerprint = async () => {
    try {
        

        // Request a new fingerprint session
        const response = await fetch('/fingerprint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error("Failed to obtain fingerprint session");
        }

        const data = await response.json();
        sessionId = data.session_id;
        
        
        console.log("New session ID:", sessionId);
        return sessionId;
    } catch (error) {
        console.error("Error getting fingerprint:", error);
        throw error;
    }
};

async function postThread() {
    try {
        const imageInput = document.getElementById('image-t');

        if (imageInput && imageInput.files && imageInput.files.length > 0) {
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

            const type = document.getElementById('new_thread_type').value;

            const postData = {
                user_token: token,
                title: title,
                content: content,
                board_id: board_id,
                date: date,
                time: time,
                type: type,
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
            uploadImage(newThreadId, null);
        } else {
            console.log('No image selected.');
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

function highlightPostWithRedirect(postId, threadId) {
    try {
        // Ensure that postId is a string, and try to find the element with the given ID
        let element = document.getElementById(postId); 

        if (!element) {
            // If the element is not found, log the error and redirect
            console.error(`Post element with ID ${postId} not found.`);
            throw new Error('Post not found');
        }

        var originalColor = element.style.backgroundColor;
        
        // Add CSS transition for smooth background color change
        element.style.transition = "background-color 0.5s ease-in-out";
        
        // Set the background color to a lighter shade
        element.style.backgroundColor = '#00ffd963';

        // After the animation, reset the background color to the original color
        setTimeout(function() {
            element.style.backgroundColor = originalColor;
        }, 400);
    } catch (error) {
        console.error(error.message); // Log the error

        // Get the current URL's search parameters
        const urlParams = new URLSearchParams(window.location.search);

        // Check if the api_key parameter exists
        const apiKey = urlParams.get('api_key');

        // Prepare the base URL for the redirection
        let redirectUrl = `/thread/${threadId.slice(1)}#${postId}`;

        
        if (apiKey) {
            redirectUrl = `/admin/thread/${threadId.slice(1)}?api_key=${apiKey}#${postId}`;
        }

        // Redirect to the thread page with the api_key if it's set
        window.location.href = redirectUrl;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash;
    if (hash) {
        const elementId = hash.replace('#', '');
        const element = document.getElementById(elementId);

        if (element) {
            setTimeout(() => {
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                history.replaceState(null, null, ' '); // Remove hash without reloading
                // Assuming threadId is available and you want to pass elementId as postId
                highlightPostWithRedirect(elementId, 't123'); // Pass threadId accordingly
            }, 100); // Delay to ensure full load
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

        const type = document.getElementById('new_reply_type').value;

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
            type: type,
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
                fileInput.value = ''
                window.location.hash = threadId ? `t${threadId}` : `r${replyId}`;
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

async function submitVote(vote, target_id, target_type){
    
    const currentDateTime = new Date();
    const year = currentDateTime.getUTCFullYear();
    const month = String(currentDateTime.getUTCMonth() + 1).padStart(2, '0');
    const day = String(currentDateTime.getUTCDate()).padStart(2, '0');
    const date = `${year}-${month}-${day}`;

    const hours = String(currentDateTime.getUTCHours()).padStart(2, '0');
    const minutes = String(currentDateTime.getUTCMinutes()).padStart(2, '0');
    const seconds = String(currentDateTime.getUTCSeconds()).padStart(2, '0');
    const time = `${hours}:${minutes}:${seconds}`;

    // User token
    const token = await getFingerprint();

    const voteData = {
        up_or_down: vote,
        user_token: token,
        date: date,
        time: time,
        thread_id: target_type == 't' ? target_id : null,
        reply_id: target_type == 'r' ? target_id : null
    };

    console.log(voteData)

    const response = await fetch(`/vote`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(voteData),
    })

    
    highlightVotes(vote + target_type + target_id)
    
}

async function highlightVotes(id) {

    if(id){
        document.getElementById(id).classList.remove('voted')
    }
    
    const token = await getFingerprint();

    const voteData = await fetch(`/vote/token/${token}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json(); // Parse JSON data
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });

    if (voteData) {
        console.log(voteData);

        for (let i = 0; i < voteData.length; i++) {
            // Access thread or reply based on the presence of 'thread' in the current voteData element
            const currentVote = voteData[i];
            if (currentVote.thread) {
                elementId = `${currentVote.up_or_down}t${currentVote.thread.id}`
                if(document.getElementById(elementId)){
                    if(currentVote.up_or_down == 0){
                        document.getElementById(`1t${currentVote.thread.id}`).classList.remove('voted')
                    }else{
                        document.getElementById(`0t${currentVote.thread.id}`).classList.remove('voted')
                    }
                    console.log(`${currentVote.up_or_down}t${currentVote.thread.id}`)
                    
                    document.getElementById(elementId).classList.add('voted')    
                }
            } else {
                elementId = `${currentVote.up_or_down}r${currentVote.reply.id}`
                if(document.getElementById(elementId)){
                    if(currentVote.up_or_down == 0){
                        document.getElementById(`1r${currentVote.reply.id}`).classList.remove('voted')
                    }else{
                        document.getElementById(`0r${currentVote.reply.id}`).classList.remove('voted')
                    }
                    console.log(`${currentVote.up_or_down}r${currentVote.reply.id}`)
                    
                    document.getElementById(elementId).classList.add('voted')
                }
            }
        }
    }
}

function maxOrMin(id, post_type){
    element = document.getElementById(`img-div-${post_type}${id}`)
    if(post_type == 't'){
        if(element.classList.contains('flex-column')){
            element.classList.remove('flex-column')
            element.getElementsByTagName('div')[0].style.maxWidth = '235px'
            element.getElementsByTagName('div')[0].style.maxHeight = 'fit-content'
        }else{
            element.classList.add('flex-column')
            element.getElementsByTagName('div')[0].style.maxWidth = 'unset';
            element.getElementsByTagName('div')[0].style.maxHeight = 'unset'
        }    
    }else{
        if(element.style.width == '30%'){
            element.style.width = 'unset'
            
            element.getElementsByTagName('img')[0].style.maxHeight = 'unset'
            element.getElementsByTagName('img')[0].style.height = 'unset'
        }else{
            element.style.width = '30%'
            
            element.getElementsByTagName('img')[0].style.maxHeight = '400px'
            element.getElementsByTagName('img')[0].style.height = 'auto'
        }  
    }
    
}

async function sortAndOrder() {
    const sort_opt = document.getElementById('sort_id').value;
    const order_opt = document.getElementById('order_id').value;

    // Get the current URL and check if api_key is already present
    const currentUrl = new URL(window.location.href);
    
    // Extract the board ID from the URL (adjust as needed based on your URL structure)
    const boardId = currentUrl.pathname.split('board/')[1]
    
    // Create the base URL, defaulting to "admin/board/" or "board/" based on api_key
    let url = new URL(currentUrl.origin + (currentUrl.searchParams.has('api_key') ? `/admin/board/${boardId}` : `/board/${boardId}`));
    
    // Get the current search parameters
    const params = new URLSearchParams(currentUrl.search);

    // Always preserve the page parameter
    if (params.has('page')) {
        url.searchParams.set('page', params.get('page'));
    }
    // If api_key exists in the current URL, add it to the new URL
    if (params.has('api_key')) {
        url.searchParams.set('api_key', params.get('api_key'));
    }

    // Add sort parameter if it's selected
    if (sort_opt) {
        url.searchParams.set('sort', sort_opt);
    }

    // Add order parameter if it's selected
    if (order_opt) {
        url.searchParams.set('order', order_opt);
    }

    // Redirect to the constructed URL
    window.location.href = url.toString();
}

async function showAll(insert_id, button_id, thread_link_id, thread_token) {
    let div = document.getElementById(button_id).getElementsByTagName('div')[0];

    if (div.style.display === 'flex') { // Use comparison instead of assignment
        div.style.display = 'none';
        document.getElementById(thread_link_id).style.display = 'none';
        document.getElementById(insert_id).style.display = 'flex';

        document.getElementById(button_id).parentElement.getElementsByTagName('span')[0].style.transition = 'opacity 0.3s ease-in-out, margin-left 0.3s ease-in-out';
        document.getElementById(button_id).parentElement.getElementsByTagName('span')[0].style.opacity = '75%'
        document.getElementById(button_id).parentElement.getElementsByTagName('span')[0].style.marginLeft = '0px'

        console.log(insert_id.slice(1, 3))
        const replyList = await fetch(`/replies/${insert_id.slice(1, 3)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json(); // Parse JSON data
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });

        const urlParams = new URLSearchParams(window.location.search);
        const api_key = urlParams.get('api_key');

        for (let i = 0; i < replyList.length - 5; i++) {
            let reply = replyList[i]; // Assuming replyList contains the necessary reply objects
        
            console.log(reply.image); // Check if image data exists

            document.getElementById(insert_id).innerHTML += `
                <div id="r${reply.id}" class="chan-${reply.type === 1 ? 'admin-' : ''}thread-info d-flex flex-column" style="min-width: 350px; width: fit-content; margin-left: ${reply.level * 14}px;">
                    <div class="d-flex justify-content-start align-content-start gap-1">
                        <div class="d-flex gap-1 align-items-center justify-content-start m-0 text-ellipsis" style="font-size: 0.7rem; color: rgba(255, 255, 255, 0.700);">
                            <span class="m-0 fw-bold" style="font-size: 0.7rem; ${reply.type === 0 ? 'color: rgba(255, 255, 255, 0.700);' : 'color: rgba(0, 255, 136);'}">
                                ${reply.type === 1 ? 'Admin:' : 'Anon:'}
                            </span>
                            <span class="m-0 text-ellipsis" style="font-size: 0.7rem; color: rgba(255, 255, 255, 0.700);">
                                ${reply.user_token}
                            </span>
                            ${reply.user_token === thread_token ? `<span class="text-info m-0 text-ellipsis" style="font-size: 0.7rem;">(OP)</span>` : ''}
                            ${reply.type === 1 ? `<img style="width: 15px; height: 15px;" src="/static/pi.svg" alt="">` : ''}
                        </div>
        
                        <hr class="m-0" style="width: 1px; border-left: solid 1px;">
                        <span class="m-0 text-ellipsis" style="font-size: 11px; color: rgba(255, 255, 255, 0.700);">Reply No.${reply.id}</span>
                        <hr class="m-0" style="width: 1px; border-left: solid 1px;">
                        <a onclick="highlightPostWithRedirect('${reply.reply_id ? 'r' + reply.reply_id : 't' + reply.thread_id}', 't${insert_id.slice(1, 3)}')" 
                           href="#${reply.reply_id ? 'r' + reply.reply_id : 't' + reply.thread_id}" 
                           class="m-0 text-ellipsis" style="font-size: 11px; color: var(--post-highlight);">
                            Replying to: ${reply.reply_id ? 'r-' + reply.reply_id : 't-' + reply.thread_id}
                        </a>
                    </div>
        
                    <p class="chan-text-content" id="format-r${reply.id}" style="min-height: ${reply.image ? '1.5rem' : '2.5rem'};"></p>
        
                    ${reply.image ? `
                        <div class="d-flex flex-column justify-content-center" style="width: 30%;" id="img-div-r${reply.id}">
                            <img class="rounded-1" style="width: 100%; height: auto; max-height: 400px;" 
                                 src="/image/${reply.image.id}" onclick="maxOrMin(${reply.id}, 'r')">
                            <div class="d-flex gap-1">
                                <span style="font-size: 0.7rem; color: #696969;" class="m-0">File: </span>
                                <a style="font-size: 0.7rem;" class="m-0 text-ellipsis" href="/image/${reply.image.id}">${reply.image.name}</a>
                            </div>
                            <span style="font-size: 0.7rem; color: #696969;" class="m-0 p-0">(${Math.floor(reply.image.size / 1024)}KB ${reply.image.measures})</span>                    
                        </div>
                    ` : ''}
        
                    <div class="d-flex justify-content-between">
                        <div class="d-flex gap-1">
                            <span class="m-0" style="font-size: 11px; color: rgba(255, 255, 255, 0.700);">
                                ${reply.date.slice(8, 10).toString()}/${reply.date.slice(5, 7).toString()}/${reply.date.slice(0, 4)}
                            </span>
                            <hr class="m-0 h-100" style="width: 1px; border-left: solid 1px;">
                            <span class="m-0" style="font-size: 11px; color: rgba(255, 255, 255, 0.700);">${reply.time} UTC</span>
                        </div>
        
                        <div class="d-flex justify-content-center gap-1">
                            <button onclick="submitVote(1, ${reply.id}, 'r')" title="${Array.isArray(reply.votes) ? reply.votes.filter(v => v.up_or_down === 1).length : 0}" 
                                    class="d-flex p-0 border-0 bg-transparent text-white" style="height: fit-content;">
                                <i class="fa-solid fa-caret-up px-1" id="1r${reply.id}" 
                                   style="font-size: 0.9rem; padding-top: 0.15rem; background-color: rgba(0, 153, 255, 0.2); border-radius: 3px; height: fit-content;"></i>
                            </button>
                            <button onclick="submitVote(0, ${reply.id}, 'r')" title="${Array.isArray(reply.votes) ? reply.votes.filter(v => v.up_or_down === 0).length : 0}" 
                                    class="d-flex p-0 border-0 bg-transparent text-white" style="height: fit-content;">
                                <i class="fa-solid fa-caret-down px-1" id="0r${reply.id}" 
                                   style="font-size: 0.9rem; padding-bottom: 0.15rem; background-color: rgba(255, 78, 78, 0.2); border-radius: 3px; height: fit-content;"></i>
                            </button>
                            <button class="d-flex gap-1 align-items-center text-white p-0 border-0 px-1" 
                                    style="background-color: rgba(0, 255, 89, 0.1); border-radius: 3px;" 
                                    onclick="replyModal('r${reply.id}')" type="button" data-bs-toggle="modal" data-bs-target="#newReply">
                                <i style="font-size: 0.7rem;" class="fa-solid fa-reply"></i>
                                <span style="font-size: 0.7rem;" class="m-0">Reply</span>   
                            </button>
                            ${api_key ? `
                                <button onclick="deletePost(${reply.id}, 'r')" class="d-flex gap-1 align-items-center text-white p-0 border-0 px-1" 
                                        style="background-color: rgba(243, 35, 35, 0.2); border-radius: 3px;" type="button">
                                    <i style="font-size: 0.7rem;" class="fa-solid fa-eraser"></i>
                                    <span style="font-size: 0.7rem;" class="m-0">Delete</span>   
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
            document.getElementById(`format-r${reply.id}`).innerHTML += reply.content    
        }
        
        
    } else {
        document.getElementById(insert_id).style.display = 'none';
        document.getElementById(insert_id).innerHTML = '';
        div.style.display = 'flex';
        document.getElementById(thread_link_id).style.display = 'flex';
        document.getElementById(button_id).parentElement.getElementsByTagName('span')[0].style.opacity = '0%'
        document.getElementById(button_id).parentElement.getElementsByTagName('span')[0].style.marginLeft = '20px'
    }
}

highlightVotes()