<template>
  <div class="outer-wrapper">
    <Navbar />

    <div class="wrapper">
      <img src="~/static/trailblazer.png" alt="">
      <h1>Welcome to Trailblazer!</h1>
    </div>
  </div>
</template>

<script>
  import Navbar from '~/components/Navbar'

  export default {
    middleware: ['anonymous'],
    components: {
      Navbar
    }
  }
</script>

<style scoped>
  .outer-wrapper {
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  .wrapper {
    flex: 1;
    background-color: hsla(339, 75%, 55%, 1);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
  }
  h1 {
    color: #fff;
  }

</style>
