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

function highlightPostWithRedirect(postId, threadId, boardId) {
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
        let redirectUrl = `/board/${boardId}/thread/${threadId.slice(1)}#${postId}`;

        
        if (apiKey) {
            redirectUrl = `/admin/board/${boardId}/thread/${threadId.slice(1)}?api_key=${apiKey}#${postId}`;
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
}

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
            element.getElementsByTagName('div')[0].style.maxWidth = 'unset'
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

        const match = insert_id.match(/^t(\d+)-all$/);
        const id = match ? match[1] : null;

        console.log(id)
        const replyList = await fetch(`/replies/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json(); // Parse JSON data
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });

        const threadData = await fetch(`/thread_data/${id}`)
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

        for (let i = 0; i < replyList.length - 5; i++) { // Loop through all items except the last 5
            let reply = replyList[i];
        
            if (reply) {
                console.log(reply.id, reply.content); // Log the ID and content of each reply to ensure they're loaded
        

                const justifyBtn = document.getElementById(`t${ id }-justify`);
                const justifyBtnbars = justifyBtn.querySelectorAll("div");
                
                document.getElementById(insert_id).innerHTML += `
                    <div id="r${reply.id}" class="chan-${reply.type === 1 ? 'admin-' : ''}thread-info d-flex flex-column ${justifyBtnbars[2].style.left === "35%" ? 'm-0' : ''}" style="min-width: 350px; width: fit-content; margin-left: ${reply.level * 14}px;">
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
                            <a
                                data-bs-toggle="tooltip" data-bs-html="true" data-bs-placement="right"
                                title='<div class="d-flex flex-column text-white">
                                    <span>${reply.reply ? reply.reply.user_token + " | Reply No." + reply.reply.id : threadData.user_token + " | Thread No." + threadData.id}</span>
                                    <hr class="my-1">
                                    <span class="fw-bold">${reply.reply ? reply.reply.content : threadData.content}</span>
                                    ${reply.reply ? (reply.reply.image ? `<img src="/image/${reply.reply.image.id}">` : '') : (threadData.image ? `<img src="/image/${threadData.image.id}">` : '')}
                                    <hr class="my-1">
                                    <span>${reply.reply ? reply.reply.date.slice(8, 10)+'/'+reply.reply.date.slice(5, 7)+'/'+reply.reply.date.slice(0, 4) : threadData.date.slice(8, 10)+'/'+threadData.date.slice(5, 7)+'/'+threadData.date.slice(0, 4)} | ${reply.reply ? reply.reply.time : threadData.time} UTC</span>
                                </div>'

                                onclick="highlightPostWithRedirect('${reply.reply_id ? 'r' + reply.reply_id : 't' + reply.thread_id}', 't${insert_id.slice(1, 3)}')"
                                id="reference-${reply.id}"
                                href="#${reply.reply_id ? 'r' + reply.reply_id : 't' + reply.thread_id}" 
                                class="m-0 text-ellipsis" style="font-size: 11px; color: var(--post-highlight);">
                                Replying to: ${reply.reply_id ? 'r-' + reply.reply_id : 't-' + reply.thread_id}
                            </a>
                        </div>
                        <p class="chan-text-content" id="format-r${reply.id}" style="min-height: ${reply.image ? '1.5rem' : '2.5rem'};"></p>
                        ${reply.image ? 
                            `<div class="d-flex flex-column justify-content-center" style="width: 30%;" id="img-div-r${reply.id}">
                                <img class="rounded-1" style="width: 100%; height: auto; max-height: 400px;" 
                                     src="/image/${reply.image.id}" onclick="maxOrMin(${reply.id}, 'r')">
                                <div class="d-flex gap-1">
                                    <span style="font-size: 0.7rem; color: #696969;" class="m-0">File: </span>
                                    <a style="font-size: 0.7rem;" class="m-0 text-ellipsis" href="/image/${reply.image.id}">${reply.image.name}</a>
                                </div>
                                <span style="font-size: 0.7rem; color: #696969;" class="m-0 p-0">(${Math.floor(reply.image.size / 1024)}KB ${reply.image.measures})</span>                    
                            </div>` : ''}
                        <div class="d-flex justify-content-between">
                            <div class="d-flex gap-1">
                                <span class="m-0" style="font-size: 11px; color: rgba(255, 255, 255, 0.700);">
                                    ${reply.date.slice(8, 10).toString()}/${reply.date.slice(5, 7).toString()}/${reply.date.slice(0, 4)}
                                </span>
                                <hr class="m-0 h-100" style="width: 1px; border-left: solid 1px;">
                                <span class="m-0" style="font-size: 11px; color: rgba(255, 255, 255, 0.700);">${reply.time} UTC</span>
                            </div>
                            <div class="d-flex justify-content-center gap-1">
                                <button onclick="submitVote(1, ${reply.id}, 'r')" data-bs-toggle="tooltip" data-bs-html="true" data-bs-placement="top" title="<span class='vote-tooltip'>${ reply.upvotes }</span>" 
                                        class="d-flex p-0 border-0 bg-transparent text-white" style="height: fit-content;">
                                    <i class="fa-solid fa-caret-up px-1" id="1r${reply.id}" 
                                       style="font-size: 0.9rem; padding-top: 0.15rem; background-color: rgba(0, 153, 255, 0.2); border-radius: 3px; height: fit-content;"></i>
                                </button>
                                <button onclick="submitVote(0, ${reply.id}, 'r')" data-bs-toggle="tooltip" data-bs-html="true" data-bs-placement="top" title="<span class='vote-tooltip'>${ reply.downvotes }</span>" 
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
                                ${api_key ? 
                                    `<button onclick="deletePost(${reply.id}, 'r')" class="d-flex gap-1 align-items-center text-white p-0 border-0 px-1" 
                                            style="background-color: rgba(243, 35, 35, 0.2); border-radius: 3px;" type="button">
                                        <i style="font-size: 0.7rem;" class="fa-solid fa-eraser"></i>
                                        <span style="font-size: 0.7rem;" class="m-0">Delete</span>   
                                    </button>` 
                                 : ''}
                            </div>
                        </div>
                    </div>
                `;
                
                document.getElementById(`format-r${reply.id}`).innerHTML += reply.content;

                
                var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl, {
                        trigger: "hover"
                    });
                });
                

            }
        }
        
        highlightVotes()
        
        
        
    } else {
        document.getElementById(insert_id).style.display = 'none';
        document.getElementById(insert_id).innerHTML = '';
        div.style.display = 'flex';
        document.getElementById(thread_link_id).style.display = 'flex';
        document.getElementById(button_id).parentElement.getElementsByTagName('span')[0].style.opacity = '0%'
        document.getElementById(button_id).parentElement.getElementsByTagName('span')[0].style.marginLeft = '20px'
    }

    

}

function justifyLeft(buttonId, threadId) {
    const button = document.getElementById(buttonId);
    if (!button) return;

    const bars = button.querySelectorAll("div");
    if (bars.length < 3) return; // Ensure there are at least 3 bars

    // Find the container element with id `t${threadId}-all`
    const containerElement = document.getElementById(`t${threadId}-all`);
    if (!containerElement) return;

    // Get the closest parent container
    const parentContainer = containerElement.closest("div");
    if (!parentContainer) return;

    // Toggle behavior
    if (bars[2].style.left === "2px") {
        // Reset to original positions
        bars[0].style.left = '2px';
        bars[1].style.left = '4px';
        bars[2].style.left = '6px';

        // Remove Bootstrap margin class (`m-0`) from all child elements of the parent container and the `t{threadId}-all` container
        parentContainer.querySelectorAll("div").forEach((child) => {
            child.classList.remove("m-0");
        });

        containerElement.querySelectorAll("div").forEach((child) => {
            child.classList.remove("m-0");
        });

        document.getElementById(`t${threadId}-link`).classList.remove("m-0")

    } else {
        // Move all bars to the left
        bars.forEach((bar) => {
            bar.style.left = "2px";
        });

        // Add Bootstrap margin class (`m-0`) to all child elements of the parent container and the `t{threadId}-all` container
        parentContainer.querySelectorAll("div").forEach((child) => {
            child.classList.add("m-0");
        });

        containerElement.querySelectorAll("div").forEach((child) => {
            child.classList.add("m-0");
        });

        document.getElementById(`t${threadId}-link`).classList.add("m-0")
    }
}

function justifyLeftThread(buttonId) {
    const button = document.getElementById(buttonId);
    if (!button) return;

    const bars = button.querySelectorAll("div");
    if (bars.length < 3) return; // Ensure there are at least 3 bars

    // Extract the thread ID from the button ID (assuming button ID is like "btn-123")
    const threadId = buttonId.match(/\d+/)?.[0]; 
    if (!threadId) return;

    // Find the thread container element with id `t{threadId}`
    const threadContainer = document.getElementById(`t${threadId}`);
    if (!threadContainer) return;

    // Select all elements whose ID starts with "r" followed by a number
    const rElements = Array.from(document.querySelectorAll('[id^="r"]'))
        .filter(el => /^r\d+$/.test(el.id));

    // Toggle behavior
    if (bars[2].style.left === "2px") {
        // Reset to original positions
        bars[0].style.left = '2px';
        bars[1].style.left = '4px';
        bars[2].style.left = '6px';

        // Remove `m-0` from thread container children
        threadContainer.querySelectorAll("div").forEach(child => {
            child.classList.remove("custom-ml");
        });

        // Remove `m-0` from elements with id matching "r" followed by a number
        rElements.forEach(el => el.classList.remove("custom-ml"));

    } else {
        // Move all bars to the left
        bars.forEach(bar => {
            bar.style.left = "2px";
        });

        

        // Add `m-0` to elements with id matching "r" followed by a number
        rElements.forEach(el => el.classList.add("custom-ml"));
    }
}


const rElements = Array.from(document.querySelectorAll('[id^="r"]'))
        .filter(el => /^r\d+$/.test(el.id));

if(rElements.length > 1){
    document.getElementById('justify-button').classList.remove('d-none')
}


async function putFingerprint() {
    const fingerprint = await getFingerprint(); // Wait for the Promise to resolve
    if(document.getElementById('thread_user_token')){
        document.getElementById('thread_user_token').value = fingerprint;
    }
    
    document.getElementById('reply_user_token').value = fingerprint; // Set the resolved value
}
putFingerprint()
highlightVotes()