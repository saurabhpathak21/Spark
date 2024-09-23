document.addEventListener('DOMContentLoaded', function () {
    const signUpForm = document.getElementById('signUpForm');
    const signInForm = document.getElementById('signInForm');
    const uploadTab = document.getElementById('upload-tab');
    const sparkspaceTab = document.getElementById('sparkspace-tab');
    const userNameInput = document.getElementById('userName');
    const signInNav = document.getElementById('sign-in-nav');
    const signUpTab = document.getElementById('sign-up-tab');
    const uploadForm = document.getElementById('uploadForm');
    const logoutBtn = document.getElementById('logoutBtn');
    const usernameDisplay = document.getElementById('username-display');
    const statusMessage = document.getElementById('statusMessage');
    const featureSections = document.querySelectorAll('.feature-section'); // Corrected selector to match class
    


    // Function to display status messages
    // function showStatusMessage(message, type = 'success') {
    //     if (statusMessage) {
    //         statusMessage.innerText = message;
    //         statusMessage.style.color = type === 'success' ? 'green' : 'red';
    //         setTimeout(() => {
    //             statusMessage.innerText = ''; // Clear the message after a short delay
    //         }, 2000);
    //     }
    // }

    const showStatusMessage = (message, type = 'success') => {
        const statusMessageDiv = document.getElementById('statusMessage');
        statusMessageDiv.className = type === 'danger' ? 'text-danger' : 'text-success';
        statusMessageDiv.textContent = message;
    };

   // Function to check the login status and update UI accordingly
   function checkLoginStatus() {
    const isLoggedIn = localStorage.getItem('loggedIn') === 'true';
    const userName = localStorage.getItem('userName');

    if (isLoggedIn && userName) {
        if (usernameDisplay) { // Check if usernameDisplay is not null
            usernameDisplay.textContent = `Welcome, ${userName}!`;
        }
        if (uploadTab) {
            uploadTab.removeAttribute('disabled');
            uploadTab.classList.add('active');
        }
        const signUpTabElement = document.getElementById('sign-up');
        if (signUpTabElement) {
            signUpTabElement.classList.remove('show', 'active');
        }
        const signInTabElement = document.getElementById('sign-in');
        if (signInTabElement) {
            signInTabElement.classList.remove('show', 'active');
        }
        const uploadElement = document.getElementById('upload');
        if (uploadElement) {
            uploadElement.classList.add('show', 'active');
        }

        // Activate SparkSpace tab after login
        if (sparkspaceTab) {
            sparkspaceTab.style.display = 'inline-block'; // Make SparkSpace tab visible
            sparkspaceTab.classList.add('active'); // Activate it
            const sparkspaceElement = document.getElementById('sparkspace'); // Content element for SparkSpace
            if (sparkspaceElement) {
                sparkspaceElement.classList.add('show', 'active'); // Show content
            }
        }

        if (signInNav) {
            signInNav.style.display = 'none';
        }
        if (logoutBtn) {
            logoutBtn.style.display = 'inline-block';
        }
        featureSections.forEach(section => {
            section.style.display = 'none';
        });
    } else {
        if (uploadTab) {
            uploadTab.setAttribute('disabled', 'true');
        }
        if (sparkspaceTab) {
            sparkspaceTab.style.display = 'none';
        }
        if (logoutBtn) {
            logoutBtn.style.display = 'none';
        }
        if (usernameDisplay) {
            usernameDisplay.textContent = '';
        }
        featureSections.forEach(section => {
            section.style.display = 'none';
        });
    }
}
// Hide logout button and reset UI for logged out state
function hideLogout() {
    console.log('Hiding logout...');
    console.log('Logout button:', logoutBtn);
    console.log('Sign-in navigation:', signInNav);
    console.log('SparkSpace tab:', sparkspaceTab);

    if (logoutBtn) {
        logoutBtn.style.display = 'none';
    }
    if (signInNav) {
        signInNav.style.display = 'block';
    }
    if (sparkspaceTab) {
        sparkspaceTab.style.display = 'none'; 
    }
}

    // Event listener for the sign-up form submission
    if (signUpForm) {
        signUpForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const fullName = document.getElementById('fullName').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();

            if (!fullName || !email || !password) {
                showStatusMessage('All fields are required.', 'danger');
                return;
            }

            try {
                const response = await fetch('/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: fullName, email, password }),
                });

                const data = await response.json();
                if (data.success) {
                    localStorage.setItem('loggedIn', 'true');
                    localStorage.setItem('userName', fullName);
                    showStatusMessage(`Welcome, ${fullName}! You can now upload your images.`, 'success');
                    checkLoginStatus();
                } else {
                    showStatusMessage(data.message || 'Sign-up failed. Please try again.', 'danger');
                }
            } catch (error) {
                console.error('Error during sign-up:', error);
                showStatusMessage('An error occurred during sign-up. Please try again later.', 'danger');
            }
        });
    }

    // Event listener for the sign-in form submission
    if (signInForm) {
        signInForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const email = document.getElementById('signInEmail').value.trim();
            const password = document.getElementById('signInPassword').value.trim();

            try {
                const response = await fetch('/signin', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();
                if (data.success) {
                    localStorage.setItem('loggedIn', 'true');
                    localStorage.setItem('userName', data.username);
                    showStatusMessage('Login successful!');
                    checkLoginStatus();
                } else {
                    showStatusMessage(data.message, 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showStatusMessage('An error occurred during sign-in.', 'danger');
            }
        });
    }

 // Event listener for the upload form

 if (uploadForm) {
    uploadForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData(this);
        const feature = document.getElementById('journey').value;
        formData.append('feature', feature);

        document.getElementById('uploading-spinner').style.display = 'block';

        try {
            const response = await fetch('/upload', { method: 'POST', body: formData });
            const data = await response.json();
            document.getElementById('uploading-spinner').style.display = 'none';

            if (data.success) {
                // Show success message
                showStatusMessage('File uploaded successfully!');

                // Enable and activate the SparkSpace tab
                sparkspaceTab.disabled = false;
                sparkspaceTab.classList.add('active');

                // Show the SparkSpace content
                const sparkspaceElement = document.getElementById('SparkSpace');
                if (sparkspaceElement) {
                    sparkspaceElement.classList.add('show', 'active');
                }

                // Optionally show feature sections
                const featureSections = document.querySelectorAll('.feature-section');
                featureSections.forEach(section => {
                    section.style.display = 'block'; // Show feature sections
                });
            } else {
                showStatusMessage(data.message || 'Upload failed.', 'danger');
            }
        } catch (error) {
            document.getElementById('uploading-spinner').style.display = 'none';
            showStatusMessage('An error occurred while uploading files.', 'danger');
            console.error('Error during file upload:', error);
        }
    });
}
   
    // Event listener for logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function () {
            const userName = localStorage.getItem('userName');
            try {
                const response = await fetch('/logout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ userName }),
                });

                const data = await response.json();
                if (data.success) {
                    localStorage.removeItem('loggedIn');
                    localStorage.removeItem('userName');
                    showStatusMessage('You have been logged out and your files have been deleted.');
                    hideLogout();
                    window.location.reload();
                } else {
                    showStatusMessage('Failed to delete user files during logout.', 'danger');
                }
            } catch (error) {
                console.error('Error during logout:', error);
                showStatusMessage('An error occurred during logout.', 'danger');
            }
        });
    }

    // Fetch uploaded image names
    async function getUploadedImageNames(userName) {
        try {
            const response = await fetch(`/get-uploaded-images?userName=${encodeURIComponent(userName)}`);
            const data = await response.json();
            return data.imageNames || [];
        } catch (error) {
            console.error('Error fetching uploaded image names:', error);
            return [];
        }
    }

    // Fetch details based on images and feature
    async function fetchDetails(imageNames, feature) {
        try {
            const response = await fetch('/process-images', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ imageNames, feature }),
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching details:', error);
            return null;
        }
    }

    // Show modal with details
    async function showModal(feature) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) loadingIndicator.style.display = 'block'; // Show loading indicator

        try {
            const userName = localStorage.getItem('userName');
            if (!userName) {
                showStatusMessage('User not logged in. Please log in to continue.', 'danger');
                return;
            }

            const imageNames = await getUploadedImageNames(userName);
            if (!imageNames || imageNames.length === 0) {
                showStatusMessage('No uploaded images found for the user.', 'danger');
                return;
            }

            const result = await fetchDetails(imageNames, feature);

            // Populate the modal content with formatted response
            if (result) {
                const formattedResponse = formatResponse(result.response);
                document.getElementById('responseContent').innerHTML = `
                    <h5>${feature}</h5>
                    <div>${formattedResponse}</div>
                `;
                // Show the modal
                new bootstrap.Modal(document.getElementById('responseModal')).show();
            } else {
                showStatusMessage('No results found.', 'danger');
            }
        } catch (error) {
            console.error('Error in showModal:', error);
            showStatusMessage('An error occurred while processing your request. Please try again.', 'danger');
        } finally {
            if (loadingIndicator) loadingIndicator.style.display = 'none'; // Hide loading indicator
        }
    }

    // Function to format the response
    function formatResponse(response) {
        const withLineBreaks = response.replace(/\n/g, '<br>');
        return withLineBreaks.replace(/- \*\*(.*?)\*\*:(.*?)(?=\n- |\n$)/gs, (match, title, content) => {
            return `<strong>${title}:</strong>${content.trim()}<br>`;
        });
    }

// Update event listeners for feature buttons, ensuring each button is correctly linked
document.querySelectorAll('.feature-section button').forEach(button => {
    button.addEventListener('click', function () {
        const feature = this.getAttribute('data-function');
        showModal(feature);
    });
});

    // Handle Sign Up / Sign In Tab Switch
    const goToSignInBtn = document.getElementById('go-to-signin');
    const goToSignUpBtn = document.getElementById('go-to-signup');

    if (goToSignInBtn) {
        goToSignInBtn.addEventListener('click', function () {
            const tab = new bootstrap.Tab(document.getElementById('sign-in-tab'));
            tab.show();
        });
    }

    if (goToSignUpBtn) {
        goToSignUpBtn.addEventListener('click', function () {
            const tab = new bootstrap.Tab(document.getElementById('sign-up-tab'));
            tab.show();
        });
    }

    // Design button functionality
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', async () => {
            const provider = document.getElementById('cloudProvider').value;
            const category = document.getElementById('architectureCategory').value;
            const details = document.getElementById('additionalDetails').value;

            document.getElementById('loading').style.display = 'block'; // Show loading indicator

            try {
                const response = await fetch('/api/generate-architecture', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ provider, category, details }),
                });

                const data = await response.json();
                displayArchitecture(data);
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('architectureOutput').innerHTML = `<p>Error generating architecture.</p>`;
            } finally {
                document.getElementById('loading').style.display = 'none'; // Hide loading indicator
            }
        });
    }

    // Display architecture
    function displayArchitecture(data) {
        const architectureOutput = document.getElementById('architectureOutput');

        // Format output
        architectureOutput.innerHTML = `
            <div class="architecture-box">
                <h2>Generated Architecture</h2>
                <pre>${data.architecture || "No architecture generated."}</pre>
            </div>
        `;
    }

    // Initialize AOS
    AOS.init();
    checkLoginStatus();
});