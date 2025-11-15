<template>
  <div class="app-container">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg main-navbar navbar-dark">
      <div class="container-fluid px-0">
        <ul class="navbar-nav w-100">
          <li class="nav-item">
            <a class="nav-link" :href="getUrl('#accounts')">
              <i class="fas fa-credit-card d-block mb-1"></i>
              Accounts & Cards
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :href="getUrl('#savings')">
              <i class="fas fa-piggy-bank d-block mb-1"></i>
              Savings & Investments
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :href="getUrl('#credit')">
              <i class="fas fa-hand-holding-usd d-block mb-1"></i>
              Loans & Financing
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :href="getUrl('#securities')">
              <i class="fas fa-chart-line d-block mb-1"></i>
              Securities Trading
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :href="getUrl('#insurance')">
              <i class="fas fa-shield-alt d-block mb-1"></i>
              Insurance
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :href="getUrl('#magazine')">
              <i class="fas fa-newspaper d-block mb-1"></i>
              Magazine
            </a>
          </li>
        </ul>
      </div>
    </nav>

    <!-- Dashboard Button -->
    <div class="dashboard-btn text-center mt-2">
      <a :href="dashboardUrl" class="btn btn-primary btn-lg">
        <i class="fas fa-home"></i> Go to Dashboard
      </a>
    </div>

    <!-- Form Container -->
    <div class="form-container mt-2">
      <form id="myForm" @submit.prevent="submitForm">
        <h2 class="text-center mb-4">User Information</h2>

        <label>Name:
          <input type="text" name="name" v-model="formData.name" @input="debouncedAutosave">
        </label>

        <label>Surname:
          <input type="text" name="surname" v-model="formData.surname" @input="debouncedAutosave">
        </label>

        <label>ID Number:
          <input type="text" name="id_number" v-model="formData.id_number" @input="debouncedAutosave">
        </label>

        <label>Job:
          <input type="text" name="job" v-model="formData.job" @input="debouncedAutosave">
        </label>

        <label>Birthday:
          <input type="date" name="birthday" v-model="formData.birthday" @input="debouncedAutosave">
        </label>

        <label>Income:
          <input type="text" name="income" v-model="formData.income" @input="debouncedAutosave">
        </label>

        <label>Address:
          <input type="text" name="address" v-model="formData.address" @input="debouncedAutosave">
        </label>

        <label>Phone Number:
          <input type="text" name="phone_number" v-model="formData.phone_number" @input="debouncedAutosave">
        </label>

        <label>Email:
          <input type="email" name="email" v-model="formData.email" @input="debouncedAutosave">
        </label>

        <div class="text-end mt-3">
          <button type="submit" class="btn btn-dark">
            Submit
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserForm',
  data() {
    return {
      formData: {
        name: '',
        surname: '',
        id_number: '',
        job: '',
        birthday: '',
        income: '',
        address: '',
        phone_number: '',
        email: ''
      },
      timeout: null,
      baseUrl: '/'
    }
  },
  computed: {
    dashboardUrl() {
      return this.baseUrl + 'dashboard';
    }
  },
  methods: {
    getUrl(section) {
      return this.baseUrl + section;
    },
    debouncedAutosave() {
      clearTimeout(this.timeout);
      this.timeout = setTimeout(this.autosave, 1000);
    },
    async autosave() {
      try {
        const response = await fetch("/api/autosave", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.formData)
        });

        if (!response.ok) {
          throw new Error('Autosave failed');
        }
      } catch (error) {
        console.error('Error during autosave:', error);
      }
    },
    async loadData() {
      try {
        const response = await fetch("/api/load");
        const data = await response.json();

        if (data) {
          Object.keys(data).forEach(key => {
            if (key in this.formData) {
              this.formData[key] = data[key] || "";
            }
          });
        }
      } catch (error) {
        console.error('Error loading data:', error);
      }
    },
    async submitForm() {
      try {
        const response = await fetch("/api/submision", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.formData)
        });

        if (response.ok) {
          // Reset form after successful submission
          Object.keys(this.formData).forEach(key => {
            this.formData[key] = '';
          });
        } else {
          throw new Error('Submission failed');
        }
      } catch (error) {
        console.error('Error submitting form:', error);
      }
    }
  },
  mounted() {
    this.loadData();
  },
  beforeUnmount() {
    clearTimeout(this.timeout);
  }
}
</script>

<style scoped>
/* Add any component-specific styles here */
.app-container {
  font-family: Arial, sans-serif;
}

.form-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

label {
  display: block;
  margin-bottom: 15px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.main-navbar {
  background-color: #343a40;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8) !important;
}

.nav-link:hover {
  color: white !important;
}
</style>