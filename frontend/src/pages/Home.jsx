import "./Home.css";
function Home(){
    return(
      <>
        <header>
          <h1>Welcome to the Home Page</h1>
          <nav>
            <ul>
              <li><a href="/">Home</a></li>
              <li><a href="/Dashbboard">Dashboard</a></li>
              <li><a href="/Login">Login</a></li>
              <li><a href="/Chat">Chat</a></li>
              <li><a href="/Profile">Profile</a></li>
            </ul>
          </nav>
      </header>
      <footer>
        <p>&copy; 2024 Meal Optimization App. All rights reserved.</p>
      </footer>
      </>
    )
}
export default Home;