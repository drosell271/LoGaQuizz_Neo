import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PlayerLogin from "./pages/player/login_player.js";
import AdminLogin from "./pages/admin/login_admin.js";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
	<React.StrictMode>
		<BrowserRouter>
			<Routes>
				<Route exact path="/" element={<PlayerLogin />} />
				<Route path="/admin" element={<AdminLogin />} />
			</Routes>
		</BrowserRouter>
	</React.StrictMode>
);
