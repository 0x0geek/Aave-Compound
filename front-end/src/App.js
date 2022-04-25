import './App.css';
import Main from "./components/Main"
import { Home, DashBoard } from './pages'
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

function App() {

    return (
        <div>
            <Router>
                <Main />
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/dashboard" element={<DashBoard />} />
                </Routes>
            </Router>
        </div>
    );
}

export default App;
