import React from "react";
import "./login_admin.css";

function LoginAdmin() {
	return (
		<div className="background_admin">
			<div className="login_card_admin">
				<div className="card_header_admin">
					<div className="card_header_admin_log">
						Bienvenido a LoGaQuiz Administrador
					</div>
				</div>
				<form>
					<div className="form_group_admin">
						<label htmlFor="username" className="label_admin">
							Usuario:
						</label>
						<input
							className="input_text_password_admin"
							required
							name="username"
							id="username"
							type="text"
						/>
					</div>
					<div className="form_group_admin">
						<label htmlFor="password" className="label_admin">
							Contraseña:
						</label>
						<input
							className="input_text_password_admin"
							required
							name="password"
							id="password"
							type="password"
						/>
					</div>
					<div className="form_group_admin">
						<input
							className="input_submit_admin"
							value="Entrar"
							type="submit"
						/>
					</div>
				</form>
			</div>
		</div>
	);
}

export default LoginAdmin;
