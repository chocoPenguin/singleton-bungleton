<template>
  <div class="login-container">
    <h2>로그인</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="email">이메일</label>
        <input v-model="email" type="email" id="email" required />
      </div>
      <div>
        <label for="password">비밀번호</label>
        <input v-model="password" type="password" id="password" required />
      </div>
      <button type="submit">로그인</button>
    </form>

    <h2>회원가입</h2>
    <form @submit.prevent="handleRegister">
      <div>
        <label for="name">이름</label>
        <input v-model="name" type="text" id="name" required />
      </div>
      <div>
        <label for="email">이메일</label>
        <input v-model="registerEmail" type="email" id="registerEmail" required />
      </div>
      <div>
        <label for="password">비밀번호</label>
        <input v-model="registerPassword" type="password" id="registerPassword" required />
      </div>
      <button type="submit">회원가입</button>
    </form>
  </div>
</template>

<script>
import { registerAuthor, loginAuthor } from "../../api/auth.js";

export default {
  name: "Login",
  data() {
    return {
      email: "",
      password: "",
      name: "",
      registerEmail: "",
      registerPassword: "",
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await loginAuthor({
          username: this.email,
          password: this.password,
        });
        localStorage.setItem("token", response.data.access_token);
        this.$router.push("/dashboard");
      } catch (err) {
        console.log(err)
        alert("Login failure: " + (err.response?.data?.detail || err.message));
      }
    },
    async handleRegister() {
      try {
        console.log(this.name, this.registerEmail, this.registerPassword);
        const response = await registerAuthor({
          name: this.name,
          email: this.registerEmail,
          password: this.registerPassword,
        });
        alert("Successfully registered! Please log in.");
        console.log(response.data);
      } catch (err) {
        alert("Register failed: " + (err.response?.data?.detail || err.message));
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: auto;
  padding: 1rem;
}
form {
  margin-bottom: 2rem;
}
label {
  display: block;
  margin-bottom: 0.3rem;
}
input {
  width: 100%;
  padding: 0.4rem;
  margin-bottom: 1rem;
}
button {
  width: 100%;
  padding: 0.5rem;
}
</style>