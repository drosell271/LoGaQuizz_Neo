import React from "react";
import "./login_player.css";

function LoginPlayer() {
	return (
		<div className="background_player">
			<div className="login_card_player">
				<div className="card_header_player">
					<div className="card_header_player_log">
						Bienvenido a LoGaQuiz Jugador
					</div>
				</div>
				<form>
					<div className="form_group_player">
						<label htmlFor="username" className="label_player">
							Nombre:
						</label>
						<input
							className="input_text_password_player"
							required
							name="username"
							id="username"
							type="text"
						/>
					</div>
					<div className="form_group_player">
						<label htmlFor="password" className="label_player">
							PIN:
						</label>
						<input
							className="input_text_password_player"
							required
							name="password"
							id="password"
							type="password"
						/>
					</div>
					<div className="form_group_player">
						<input
							className="input_submit_player"
							value="Entrar"
							type="submit"
						/>
					</div>
				</form>
			</div>
		</div>
	);
}

export default LoginPlayer;
