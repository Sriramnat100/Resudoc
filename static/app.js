const API_BASE = 'http://localhost:8000';
const USER_ID = 'bb8c3e4a-d9e5-5a19-8a2e-c5a8e3f4e5d6'; // Default user ID

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const uploadBtn = document.getElementById('uploadBtn');
const tagInput = document.getElementById('tagInput');
const jdInput = document.getElementById('jdInput');
const topKSelect = document.getElementById('topK');
const matchBtn = document.getElementById('matchBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsDiv = document.getElementById('results');
const loadingOverlay = document.getElementById('loadingOverlay');
const folderList = document.getElementById('folderList');
const tagFilters = document.getElementById('tagFilters');

let selectedFiles = [];
let folders = [];

// Load folders on page load
window.addEventListener('DOMContentLoaded', loadFolders);

async function loadFolders() {
    try {
        // Load folders (tags)
        const foldersResponse = await fetch(`${API_BASE}/folders?user_id=${USER_ID}`);
        const foldersData = await foldersResponse.json();
        folders = foldersData.folders || [];

        // Load total resume count
        const resumesResponse = await fetch(`${API_BASE}/resumes?user_id=${USER_ID}`);
        const resumesData = await resumesResponse.json();
        const totalCount = resumesData.total || 0;

        renderFolders(totalCount);
        renderTagFilters();
    } catch (error) {
        console.error('Error loading folders:', error);
    }
}

function renderFolders(totalCount) {
    // Update "All Resumes" count with actual total
    document.getElementById('allCount').textContent = totalCount;

    // Remove existing folder items (except "All")
    const existingFolders = folderList.querySelectorAll('.folder-item:not(.all-folder)');
    existingFolders.forEach(f => f.remove());

    // Add folder items
    folders.forEach((folder, index) => {
        const folderItem = document.createElement('div');
        folderItem.className = 'folder-item';
        folderItem.dataset.tag = folder.name;
        folderItem.innerHTML = `
            <span><span class="folder-number">${index + 1}.</span> 📁 ${folder.name}</span>
            <span class="folder-count">${folder.count}</span>
        `;
        folderList.appendChild(folderItem);
    });

    // Add click handlers to all folder items
    document.querySelectorAll('.folder-item').forEach(item => {
        item.addEventListener('click', () => {
            // Update active state
            document.querySelectorAll('.folder-item').forEach(f => f.classList.remove('active'));
            item.classList.add('active');

            // Load resumes for this tag
            const tag = item.dataset.tag;
            loadResumes(tag);
        });
    });
}

async function loadResumes(tag = '') {
    const resumeListSection = document.getElementById('resumeListSection');
    const resumeListTitle = document.getElementById('resumeListTitle');
    const resumeList = document.getElementById('resumeList');

    try {
        const response = await fetch(`${API_BASE}/resumes?user_id=${USER_ID}`);
        const data = await response.json();
        let resumes = data.resumes || [];

        // Filter by tag if specified
        if (tag) {
            resumes = resumes.filter(resume => {
                const resumeTags = resume.tags || [];
                return resumeTags.includes(tag);
            });
            resumeListTitle.textContent = `📁 ${tag}`;
        } else {
            resumeListTitle.textContent = '📋 All Resumes';
        }

        // Show section
        resumeListSection.style.display = 'block';

        // Render resumes
        if (resumes.length === 0) {
            resumeList.innerHTML = '<p style="color: var(--text-muted);">No resumes found' + (tag ? ` with tag "${tag}"` : '') + '.</p>';
        } else {
            resumeList.innerHTML = resumes.map((resume, index) => `
                <div class="resume-item">
                    <div class="resume-item-info">
                        <div class="resume-item-name">
                            <span class="resume-number">${index + 1}.</span> 📄 ${resume.filename}
                        </div>
                        ${resume.tags && resume.tags.length > 0 ? `
                            <div class="resume-item-tags">
                                ${resume.tags.map(t => `<span class="resume-tag">${t}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                    <button class="resume-item-delete" onclick="deleteResume('${resume.resume_id}')">Delete</button>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading resumes:', error);
    }
}

async function deleteResume(resumeId) {
    if (!confirm('Are you sure you want to delete this resume?')) return;

    try {
        const response = await fetch(`${API_BASE}/resumes/${resumeId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('✅ Resume deleted successfully!');
            // Reload current view
            const activeFolder = document.querySelector('.folder-item.active');
            const tag = activeFolder ? activeFolder.dataset.tag : '';
            await loadResumes(tag);
            await loadFolders();
        } else {
            alert('❌ Error deleting resume');
        }
    } catch (error) {
        alert('❌ Error deleting resume: ' + error.message);
    }
}

// Make deleteResume globally accessible
window.deleteResume = deleteResume;


function renderTagFilters() {
    // Clear existing filters except "All"
    tagFilters.innerHTML = `
        <label class="tag-checkbox">
            <input type="checkbox" value="" checked> All
        </label>
    `;

    // Add tag filter checkboxes
    folders.forEach(folder => {
        const label = document.createElement('label');
        label.className = 'tag-checkbox';
        label.innerHTML = `
            <input type="checkbox" value="${folder.name}"> ${folder.name}
        `;
        tagFilters.appendChild(label);
    });

    // Handle "All" checkbox logic
    const allCheckbox = tagFilters.querySelector('input[value=""]');
    const otherCheckboxes = tagFilters.querySelectorAll('input[value]:not([value=""])');

    allCheckbox.addEventListener('change', () => {
        if (allCheckbox.checked) {
            otherCheckboxes.forEach(cb => cb.checked = false);
        }
    });

    otherCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            if (cb.checked) {
                allCheckbox.checked = false;
            }
            // If no checkboxes are checked, check "All"
            const anyChecked = Array.from(otherCheckboxes).some(c => c.checked);
            if (!anyChecked) {
                allCheckbox.checked = true;
            }
        });
    });
}

// Upload Area Click
uploadArea.addEventListener('click', () => fileInput.click());

// Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');
    addFiles(files);
});

// File Input Change
fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    addFiles(files);
});

// Add Files
function addFiles(files) {
    selectedFiles = [...selectedFiles, ...files];
    renderFileList();
    uploadBtn.disabled = selectedFiles.length === 0;
}

// Remove File
function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderFileList();
    uploadBtn.disabled = selectedFiles.length === 0;
}

// Render File List
function renderFileList() {
    if (selectedFiles.length === 0) {
        fileList.innerHTML = '';
        return;
    }

    fileList.innerHTML = selectedFiles.map((file, index) => `
        <div class="file-item">
            <span>📄 ${file.name}</span>
            <button onclick="removeFile(${index})">✕</button>
        </div>
    `).join('');
}

// Upload Resumes
uploadBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;

    showLoading();

    const formData = new FormData();
    selectedFiles.forEach(file => formData.append('files', file));
    formData.append('user_id', USER_ID);
    formData.append('tags', tagInput.value); // Comma-separated tags

    try {
        const response = await fetch(`${API_BASE}/resumes/upload-batch`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        hideLoading();

        if (data.success_count > 0) {
            alert(`✅ Successfully uploaded ${data.success_count} resume(s)!`);
            selectedFiles = [];
            renderFileList();
            uploadBtn.disabled = true;
            fileInput.value = '';
            tagInput.value = '';

            // Reload folders
            await loadFolders();
        }

        if (data.failure_count > 0) {
            alert(`⚠️ ${data.failure_count} file(s) failed to upload.`);
        }
    } catch (error) {
        hideLoading();
        alert('❌ Error uploading resumes: ' + error.message);
    }
});

// Match Job Description
matchBtn.addEventListener('click', async () => {
    const jdText = jdInput.value.trim();

    if (!jdText) {
        alert('Please enter a job description');
        return;
    }

    // Get selected tags
    const selectedTags = Array.from(tagFilters.querySelectorAll('input:checked'))
        .map(cb => cb.value)
        .filter(v => v !== ''); // Exclude "All"

    showLoading();

    try {
        const requestBody = {
            user_id: USER_ID,
            jd_text: jdText,
            k: parseInt(topKSelect.value)
        };

        // Only add tags if specific tags are selected (not "All")
        if (selectedTags.length > 0) {
            requestBody.tags = selectedTags;
        }

        const response = await fetch(`${API_BASE}/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        hideLoading();

        if (data.results && data.results.length > 0) {
            displayResults(data.results);
        } else {
            alert('No matching resumes found. Upload some resumes first!');
        }
    } catch (error) {
        hideLoading();
        alert('❌ Error matching resumes: ' + error.message);
    }
});

// Display Results
function displayResults(results) {
    resultsSection.style.display = 'block';

    resultsDiv.innerHTML = results.map((result, index) => {
        const scoreColor = result.score >= 80 ? 'var(--success)' :
            result.score >= 60 ? 'var(--warning)' :
                'var(--danger)';

        return `
            <div class="result-card">
                <div class="result-header">
                    <div>
                        <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.25rem;">
                            #${index + 1}
                        </div>
                        <div class="result-title">${result.filename}</div>
                    </div>
                    <div class="result-score" style="color: ${scoreColor};">
                        ${result.score.toFixed(0)}
                    </div>
                </div>

                <div class="result-reasoning">
                    ${result.reasoning}
                </div>

                ${result.key_matches && result.key_matches.length > 0 ? `
                    <div class="tag-label">✅ Key Matches</div>
                    <div class="result-tags">
                        ${result.key_matches.map(match => `
                            <span class="tag tag-match">${match}</span>
                        `).join('')}
                    </div>
                ` : ''}

                ${result.gaps && result.gaps.length > 0 ? `
                    <div class="tag-label">⚠️ Gaps</div>
                    <div class="result-tags">
                        ${result.gaps.map(gap => `
                            <span class="tag tag-gap">${gap}</span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Loading Overlay
function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// Make removeFile globally accessible
window.removeFile = removeFile;
