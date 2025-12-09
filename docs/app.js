// myPMO Agent Dashboard JavaScript

// Cloud Functions API URL
const API_URL = 'https://us-central1-my-pmo-agent-v1.cloudfunctions.net/my-pmo-agent';

// Command switching
document.querySelectorAll('.cmd-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Update active button
        document.querySelectorAll('.cmd-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Show corresponding form
        const cmd = btn.dataset.cmd;
        document.querySelectorAll('.form-container').forEach(form => form.classList.add('hidden'));
        document.getElementById(`${cmd}-form`).classList.remove('hidden');

        // Hide response
        document.getElementById('response-section').classList.add('hidden');
    });
});

// Ask Query
async function askQuery() {
    const query = document.getElementById('query').value.trim();

    if (!query) {
        alert('質問を入力してください');
        return;
    }

    const payload = {
        message: {
            text: `/ask ${query}`
        }
    };

    await sendRequest(payload);
}

// Check Risks
async function checkRisks() {
    const payload = {
        message: {
            text: '/risk-alert'
        }
    };

    await sendRequest(payload);
}

// Update Issue
async function updateIssue() {
    const category = document.getElementById('category').value.trim();
    const content = document.getElementById('content').value.trim();
    const vendor = document.getElementById('vendor').value.trim();
    const assignee = document.getElementById('assignee').value.trim();
    const priority = document.getElementById('priority').value;
    const deadline = document.getElementById('deadline').value;
    const impact = document.getElementById('impact').value.trim();

    if (!category || !content || !vendor || !assignee || !deadline) {
        alert('必須項目を入力してください（カテゴリ、内容、ベンダー名、担当者、期限）');
        return;
    }

    const issueData = `${category}|${content}|${vendor}|${assignee}|${priority}|${deadline}|${impact}`;

    const payload = {
        message: {
            text: `/update-issue ${issueData}`
        }
    };

    await sendRequest(payload);
}

// Send Request to Cloud Functions
async function sendRequest(payload) {
    const loading = document.getElementById('loading');
    const responseSection = document.getElementById('response-section');
    const responseContent = document.getElementById('response-content');

    // Show loading
    loading.classList.remove('hidden');
    responseSection.classList.add('hidden');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display response
        loading.classList.add('hidden');
        responseSection.classList.remove('hidden');

        if (data.text) {
            responseContent.textContent = data.text;
        } else {
            responseContent.textContent = JSON.stringify(data, null, 2);
        }

        // Scroll to response
        responseSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        loading.classList.add('hidden');
        responseSection.classList.remove('hidden');
        responseContent.textContent = `❌ エラーが発生しました:\n\n${error.message}\n\nCloud Functionsが正常に動作しているか確認してください。`;
        responseContent.style.color = '#ea4335';
    }
}

// Initialize: Set today's date for deadline field
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('deadline').value = today;
});
