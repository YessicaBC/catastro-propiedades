import streamlit as st
from datetime import datetime

def mostrar_perfil_usuario():
    st.markdown("""
    <style>
        .perfil-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .header-perfil {
            text-align: center;
            margin-bottom: 2rem;
        }
        .avatar {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 1rem;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 3rem;
            font-weight: 600;
        }
        .stats-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin: 2rem 0;
        }
        .stat-card {
            background: #f8fafc;
            padding: 1.25rem;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e293b;
            margin: 0.5rem 0 0.25rem;
        }
        .stat-label {
            font-size: 0.875rem;
            color: #64748b;
        }
        .seccion {
            margin-bottom: 2rem;
        }
        .seccion-titulo {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f1f5f9;
        }
        .info-item {
            display: flex;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #f1f5f9;
        }
        .info-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background: #f1f5f9;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            color: #3b82f6;
        }
        .info-content {
            flex: 1;
        }
        .info-label {
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.25rem;
        }
        .info-value {
            font-size: 0.95rem;
            color: #1e293b;
            font-weight: 500;
        }
        .btn-editar {
            background: #f1f5f9;
            border: none;
            color: #3b82f6;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            margin-left: auto;
        }
        .btn-editar i {
            margin-right: 0.5rem;
        }
        .badge-rol {
            display: inline-block;
            background: #e0f2fe;
            color: #0369a1;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="perfil-container">
        <div class="header-perfil">
            <div class="avatar">
                <span>JD</span>
            </div>
            <h1 style="margin: 0.5rem 0 0.25rem; color: #1e293b;">Juan Delgado</h1>
            <p style="margin: 0; color: #64748b; font-size: 1rem;">
                Administrador del Sistema
                <span class="badge-rol">Administrador</span>
            </p>
            <p style="margin: 0.5rem 0 0; color: #94a3b8; font-size: 0.9rem;">
                <i class="fas fa-map-marker-alt" style="margin-right: 0.5rem;"></i>
                Municipalidad de Independencia
            </p>
        </div>

        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-value">156</div>
                <div class="stat-label">Propiedades</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">1,248</div>
                <div class="stat-label">Visitas</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">98%</div>
                <div class="stat-label">Completado</div>
            </div>
        </div>

        <div class="seccion">
            <h2 class="seccion-titulo">Información Personal</h2>
            
            <div class="info-item">
                <div class="info-icon">
                    <i class="fas fa-envelope"></i>
                </div>
                <div class="info-content">
                    <div class="info-label">Correo Electrónico</div>
                    <div class="info-value">juan.delgado@independencia.cl</div>
                </div>
                <button class="btn-editar">
                    <i class="fas fa-pen"></i> Editar
                </button>
            </div>

            <div class="info-item">
                <div class="info-icon">
                    <i class="fas fa-phone"></i>
                </div>
                <div class="info-content">
                    <div class="info-label">Teléfono</div>
                    <div class="info-value">+56 9 1234 5678</div>
                </div>
                <button class="btn-editar">
                    <i class="fas fa-pen"></i> Editar
                </button>
            </div>

            <div class="info-item">
                <div class="info-icon">
                    <i class="fas fa-briefcase"></i>
                </div>
                <div class="info-content">
                    <div class="info-label">Departamento</div>
                    <div class="info-value">Catastro y Propiedades</div>
                </div>
                <button class="btn-editar">
                    <i class="fas fa-pen"></i> Editar
                </button>
            </div>
        </div>

        <div class="seccion">
            <h2 class="seccion-titulo">Preferencias</h2>
            
            <div class="info-item">
                <div class="info-icon">
                    <i class="fas fa-moon"></i>
                </div>
                <div class="info-content">
                    <div class="info-label">Tema</div>
                    <div class="info-value">Claro</div>
                </div>
                <button class="btn-editar">
                    <i class="fas fa-pen"></i> Cambiar
                </button>
            </div>

            <div class="info-item">
                <div class="info-icon">
                    <i fa-bell"></i>
                </div>
                <div class="info-content">
                    <div class="info-label">Notificaciones</div>
                    <div class="info-value">Activadas</div>
                </div>
                <button class="btn-editar">
                    <i class="fas fa-pen"></i> Configurar
                </button>
            </div>
        </div>

        <div class="seccion">
            <h2 class="seccion-titulo">Seguridad</h2>
            
            <div class="info-item">
                <div class="info-icon">
                    <i class="fas fa-key"></i>
                </div>
                <div class="info-content">
                    <div class="info-label">Contraseña</div>
                    <div class="info-value">•••••••••••</div>
                </div>
                <button class="btn-editar">
                    <i class="fas fa-pen"></i> Cambiar
                </button>
            </div>

            <div class="info-item">
                <div class="info-icon" style="background: #fef2f2; color: #dc2626;">
                    <i class="fas fa-sign-out-alt"></i>
                </div>
                <div class="info-content">
                    <div class="info-label">Sesión</div>
                    <div class="info-value">Activa desde hoy a las 08:45 AM</div>
                </div>
                <button class="btn-editar" style="color: #dc2626;">
                    <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                </button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Para probar el componente
if __name__ == "__main__":
    mostrar_perfil_usuario()
