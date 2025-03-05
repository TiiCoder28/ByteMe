<template>
  <div class="chat-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="avatar-container">
        <div class="avatar">
          <svg class="avatar-icon" viewBox="0 0 24 24" fill="currentColor">
            <rect x="4" y="6" width="16" height="12" rx="4" ry="4" fill="#3b82f6"/>
            <circle cx="8" cy="10" r="1.5" fill="white"/>
            <circle cx="16" cy="10" r="1.5" fill="white"/>
            <path d="M6 17c2 2 12 2 14 0" stroke="white" stroke-width="2" fill="none"/>
          </svg>
        </div>
      </div>
      <!-- Chat History -->
      <div class="chat-history">
        <h3 class="text-xl font-bold mb-4">Chat History</h3>
        <ul>
          <li v-for="(message, index) in messages.slice(-5)" :key="index" class="chat-history-item">
            {{ message.text }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Chat Window -->
    <div class="chat-window">
      <div class="messages-container">
        <div v-for="(message, index) in messages" :key="index" class="message-container" :class="{'user-message': message.isUser}">
          <div class="message" :class="message.isUser ? 'user' : 'bot'">
            {{ message.text }}
          </div>
        </div>
      </div>

      <!-- Input Box -->
      <div class="input-container">
        <input v-model="newMessage" type="text" placeholder="Type a message..." class="input-box">
        <button @click="sendMessage" class="send-btn">Send</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      messages: [
        { text: "Hello! I am your recruitment assistant. Please provide a job description or share your qualifications, and I will assist you!", isUser: false },
      ],
      newMessage: "",
      isRecruiter: true, // Switch this flag based on the user's type (Recruiter or Candidate)
    };
  },
  methods: {
    async sendMessage() {
      if (this.newMessage.trim() === "") return;

      // Add user's message
      this.messages.push({ text: this.newMessage, isUser: true });
      const userMessage = this.newMessage;
      this.newMessage = "";

      // Determine whether it's a job search or candidate search
      const apiUrl = this.isRecruiter
        ? "http://localhost:8000/find_candidates"
        : "http://localhost:8000/find_jobs";

      // Make the API call to the appropriate endpoint
      try {
        const response = await axios.post(apiUrl, {
          job_description: userMessage
        });

        // Handle no results
        if (!response.data.candidates && !response.data.jobs) {
          this.messages.push({ text: "Sorry, no results found.", isUser: false });
          return;
        }

        // Handle recruiter case
        if (this.isRecruiter && response.data.candidates) {
          let candidateMessages = "Top candidates found:\n";
          response.data.candidates.forEach((candidate) => {
            candidateMessages += `Name: ${candidate.name}\nQualifications: ${candidate.qualifications}\nCertifications: ${candidate.certifications}\nExperience: ${candidate.experience}\n\n`;
          });
          this.messages.push({ text: candidateMessages, isUser: false });
        }

        // Handle candidate case
        if (!this.isRecruiter && response.data.jobs) {
          let jobMessages = "Top job matches:\n";
          response.data.jobs.forEach((job) => {
            jobMessages += `Job Title: ${job.name_of_job}\nExperience Required: ${job.experience_required}\nQualifications Required: ${job.education_required}\nSkills Required: ${job.skills_required}\nPreferred Qualifications: ${job.preferred_qualifications}\n\n`;
          });
          this.messages.push({ text: jobMessages, isUser: false });
        }

      } catch (error) {
        this.messages.push({ text: "Error fetching data, please try again.", isUser: false });
      }
    },
  },
};
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  width: 100%;
  padding: 16px;
}

.sidebar {
  width: 25%;
  background-color: white;
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.avatar-container {
  display: flex;
  justify-content: center;
}

.avatar {
  width: 96px;
  height: 96px;
  background-color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-bottom: 16px;
}

.avatar-icon {
  width: 64px;
  height: 64px;
  color: white;
}

.chat-history {
  margin-top: 16px;
}

.chat-history h3 {
  font-size: 18px;
  font-weight: bold;
}

.chat-history-item {
  background-color: #f3f4f6;
  margin-bottom: 8px;
  padding: 8px;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
}

.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-left: 16px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 16px;
}

.message-container {
  display: flex;
  margin-bottom: 8px;
}

.message-container.user-message {
  justify-content: flex-end;
}

.message {
  padding: 12px;
  border-radius: 8px;
  max-width: 250px;
  font-size: 14px;
}

.message.user {
  background-color: #3b82f6;
  color: white;
}

.message.bot {
  background-color: #e5e7eb;
  color: black;
}

.input-container {
  display: flex;
  align-items: center;
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
}

.input-box {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  margin-right: 16px;
}

.send-btn {
  background-color: #3b82f6;
  color: white;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 10px;
}
</style>
