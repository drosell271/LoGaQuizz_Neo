import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import reportWebVitals from "./reportWebVitals";
import Login from "./login";
import MenuTest from "./menu_test";
import MenuJugadores from "./menu_jugadores";
import DetalleTest from "./test_view";
import EditTest from "./test_edit";
import CreateTest from "./test_create";
import PlayerSummary from "./player_summary";
import TestSummary from "./test_summary";
import TestGameDetails from "./game_by_test";
import PlayerGameDetails from "./game_by_player";
import "bootstrap/dist/css/bootstrap.min.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
	<React.StrictMode>
		<BrowserRouter>
			<Routes>
				<Route path="/login" element={<Login />} />
				<Route path="/menu/test" element={<MenuTest />} />
				<Route path="/menu/players" element={<MenuJugadores />} />
				<Route path="/menu/test/:id" element={<DetalleTest />} />
				<Route path="/menu/test/:id/edit" element={<EditTest />} />
				<Route path="/menu/test/new" element={<CreateTest />} />
				<Route path="/menu/player/:id" element={<PlayerSummary />} />
				<Route path="/menu/test/:id/games" element={<TestSummary />} />
				<Route
					path="/menu/test/:testid/game/:gameid"
					element={<TestGameDetails />}
				/>
				<Route
					path="/menu/player/:id_player/game/:id_game"
					element={<PlayerGameDetails />}
				/>
				{/* Puedes agregar más rutas según sea necesario */}
			</Routes>
		</BrowserRouter>
	</React.StrictMode>
);

reportWebVitals();
