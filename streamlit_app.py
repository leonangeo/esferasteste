import streamlit as st                  #---Núcleo é streamlit, framework para visualização gráfica no navegador
import numpy as np                      #---Lib geral de matemática
import plotly.graph_objects as go       #---Lib de plot de gráficos

#---Configuração da página para usar a largura total e definir o título da aba
st.set_page_config(page_title="Simulador de Refração", layout="wide")

# ==========================================
# PAINEL LATERAL (Equivalente aos 25% da esquerda)
# ==========================================
with st.sidebar:
    G = st.sidebar.radio("Geometria [m]:", [15, 30], horizontal=True)
    R = st.slider("Raio da Esfera [R,μm]", min_value=50, max_value=2000, value=1000, step=1)
    I = st.slider("Índice de refração [I,escalar]", min_value=1.4, max_value=2.5, value=1.5, step=0.01)
    A_seg = st.slider("Inclinação da tinta [graus]", min_value=0.0, max_value=60.0, value=0.0, step=0.1)
    Anc = st.slider("Ancoragem [porcentagem]", min_value=40.0, max_value=70.0, value=50.0, step=1.0)
    T1 = st.slider("Ponto de contato 1 [P1,radianos]", min_value=0.0, max_value=float(np.pi / 2), value=0.78, step=0.01)
    T2 = st.slider("Ponto de contato 2 [P2,radianos]", min_value=0.0, max_value=float(np.pi / 2), value=0.50, step=0.01)
    st.markdown("<h3 style='text-align: center;'>Recepção (Olho)</h3>", unsafe_allow_html=True)
    L_arco_cm = st.slider("Tamanho do arco visual [cm]", min_value=1.0, max_value=50.0, value=4.0, step=0.1)
    st.divider()

    st.markdown("<h3 style='text-align: center;'>Resultados</h3>", unsafe_allow_html=True)
    st.markdown(f"**Raio atual da esfera:** {R} μm")
    resultado_luz = st.empty()  # ---Espaço reservado para a porcentagem de luz
    st.divider()

# ==========================================
# CÁLCULOS MATEMÁTICOS
# ==========================================
# ---1. Esfera (Círculo parametrizado)
theta = np.linspace(0, 2 * np.pi, 256)  # ---Matriz de ângulos para desenhar o círculo
x_circle = R * np.cos(theta)  # ---Coordenadas X da esfera
y_circle = R * np.sin(theta)  # ---Coordenadas Y da esfera

# ---2. Segmento de reta central (Faixa de tinta) e Cálculo da Interseção
L_seg = 1.1 * (2 * R)  # ---Tamanho total do segmento de tinta
A_seg_rad = np.radians(-A_seg)  # ---Converte para radianos e inverte o sinal

# ---Cálculo do deslocamento por Ancoragem
d_offset = R * (2.0 * Anc / 100.0 - 1.0)  # ---Distância do centro até a reta

# ---Vetor normal apontando para o 1º quadrante (para onde a luz vem)
nx = -np.sin(A_seg_rad)
ny = np.cos(A_seg_rad)

# ---Deslocamento X e Y da reta ao longo do vetor normal
shift_x = d_offset * nx
shift_y = d_offset * ny

# ---Equação do segmento transladado
x_seg = [- (L_seg / 2) * np.cos(A_seg_rad) + shift_x, (L_seg / 2) * np.cos(A_seg_rad) + shift_x]
y_seg = [- (L_seg / 2) * np.sin(A_seg_rad) + shift_y, (L_seg / 2) * np.sin(A_seg_rad) + shift_y]
#---Cálculo da linha do Asfalto (Horizontal, passando pelo centro da tinta)
L_asfalto = 1.4 * (2 * R)                           #---Tamanho total de 1.4x o diâmetro da esfera
x_asfalto = [shift_x - (L_asfalto / 2), shift_x + (L_asfalto / 2)]
y_asfalto = [shift_y, shift_y]                      #---Mantém a altura Y constante (horizontal)
# ---Encontrando o ponto de ancoragem mais à direita (Ponto zero para os controles deslizantes)
theta_N = np.arctan2(ny, nx)  # ---Ângulo do vetor normal da tinta
theta_C = np.arccos(np.clip(d_offset / R, -1.0, 1.0))  # ---Abertura angular da área exposta (com trava de proteção)
theta_zero = theta_N - theta_C  # ---Ponto de interseção mais à direita

# ---3 e 4. Vetores de Incidência e Mapeamento da Área Máxima da Esfera
X_O = float(G) * 10 ** 6
Y_O = 0.65 * 10 ** 6
A_rad_common = np.arctan2(Y_O, X_O)
length = (3 / 4) * R

# Identificando o limite máximo de área permitida na esfera
theta_tangente = A_rad_common + (np.pi / 2)       # Ponto onde o raio passa raspando no topo
theta_tinta_max = theta_N + theta_C               # O outro lado da interseção com a tinta
theta_max_permitido = min(theta_tangente, theta_tinta_max)

# Fator de escala: mapeia o slider [0 até pi/2] para a área real disponível [theta_zero até theta_max]
faixa_disponivel = max(0.0, theta_max_permitido - theta_zero)
fator_escala = faixa_disponivel / (np.pi / 2)

# Pontos P1 e P2 na superfície
T1_calc = theta_zero + (T1 * fator_escala)
px1 = R * np.cos(T1_calc)
py1 = R * np.sin(T1_calc)

T2_calc = theta_zero + (T2 * fator_escala)
px2 = R * np.cos(T2_calc)
py2 = R * np.sin(T2_calc)

vx1 = [px1 + length * np.cos(A_rad_common), px1]
vy1 = [py1 + length * np.sin(A_rad_common), py1]

vx2 = [px2 + length * np.cos(A_rad_common), px2]
vy2 = [py2 + length * np.sin(A_rad_common), py2]

# ---5. Refração na Esfera (Lei de Snell) e Reflexão Interna
F1 = A_rad_common - T1_calc  # ---Ângulo de incidência F1
D1 = np.arcsin(np.clip(np.sin(F1) / I, -1.0, 1.0))  # ---Lei de Snell com trava de segurança

#---Cálculo de Fresnel Entrada (P1 -> Q1)
n1_in = 1.0                                         #---Índice de fora (ar)
n2_in = I                                           #---Índice de dentro (esfera)
cos_i_in = np.cos(F1)                               #---Cosseno do ângulo de incidência
cos_t_in = np.cos(D1)                               #---Cosseno do ângulo de refração

Rs_in = abs((n1_in * cos_i_in - n2_in * cos_t_in) / (n1_in * cos_i_in + n2_in * cos_t_in))**2
Rp_in = abs((n1_in * cos_t_in - n2_in * cos_i_in) / (n1_in * cos_t_in + n2_in * cos_i_in))**2
T_frac_in = 1.0 - ((Rs_in + Rp_in) / 2)             #---Fração de luz que entra (valor de 0 a 1)

TQ1 = T1_calc + np.pi + 2 * D1  # ---Refração Q1
qx1 = R * np.cos(TQ1)
qy1 = R * np.sin(TQ1)

TR1 = TQ1 + np.pi + 2 * D1  # ---Reflexão interna R1
rx1 = R * np.cos(TR1)
ry1 = R * np.sin(TR1)

F2 = A_rad_common - T2_calc  # ---Ângulo de incidência F2
D2 = np.arcsin(np.clip(np.sin(F2) / I, -1.0, 1.0))  # ---Lei de Snell com trava de segurança

TQ2 = T2_calc + np.pi + 2 * D2  # ---Refração Q2
qx2 = R * np.cos(TQ2)
qy2 = R * np.sin(TQ2)

TR2 = TQ2 + np.pi + 2 * D2  # ---Reflexão interna R2
rx2 = R * np.cos(TR2)
ry2 = R * np.sin(TR2)

#---6. Saída do Raio da Esfera (Refração Snell e Fresnel de Saída)
#---Para o Raio 1 (Saindo em R1 para S1)
ang_in1 = np.arctan2(ry1 - qy1, rx1 - qx1)          #---Ângulo absoluto do raio dentro da esfera (Q1 -> R1)
ang_diff1 = ang_in1 - TR1                           #---Ângulo de incidência interno (Raio vs Normal)

ang_out1_diff = np.arcsin(np.clip(I * np.sin(ang_diff1), -1.0, 1.0)) #---Ângulo de refração externo (Lei de Snell)
ang_out1 = TR1 + ang_out1_diff                      #---Direção absoluta do raio saindo

sx1 = rx1 + length * np.cos(ang_out1)               #---Coordenada X do ponto S1 (Tamanho igual ao de entrada)
sy1 = ry1 + length * np.sin(ang_out1)               #---Coordenada Y do ponto S1

#---Cálculo de Fresnel Saída (R1 -> S1)
n1_out = I                                          #---Agora a luz vem de DENTRO (Vidro)
n2_out = 1.0                                        #---E vai para FORA (Ar)
cos_i_out = np.cos(ang_diff1)                       #---Cosseno do ângulo de incidência (interno)
cos_t_out = np.cos(ang_out1_diff)                   #---Cosseno do ângulo de refração (externo)

Rs_out = abs((n1_out * cos_i_out - n2_out * cos_t_out) / (n1_out * cos_i_out + n2_out * cos_t_out))**2
Rp_out = abs((n1_out * cos_t_out - n2_out * cos_i_out) / (n1_out * cos_t_out + n2_out * cos_i_out))**2
T_frac_out = 1.0 - ((Rs_out + Rp_out) / 2)          #---Fração de luz que sai (valor de 0 a 1)

#---Para o Raio 2 (Saindo em R2 para S2)
ang_in2 = np.arctan2(ry2 - qy2, rx2 - qx2)
ang_diff2 = ang_in2 - TR2
ang_out2 = TR2 + np.arcsin(np.clip(I * np.sin(ang_diff2), -1.0, 1.0))

sx2 = rx2 + length * np.cos(ang_out2)
sy2 = ry2 + length * np.sin(ang_out2)

#---7. Cálculo da Densidade de Luz na Tela de 15m
R_15 = float(G) * 10**6                                 #---Raio de 15m convertido para μm
L_arco_um = L_arco_cm * 10**4                       #---Converte cm para μm (1 cm = 10,000 μm)

#---Posição do olho a 1.2m de altura no círculo de 15m
y_eye = 1.2 * 10**6                                 #---Altura 1.2m em μm
x_eye = np.sqrt(R_15**2 - y_eye**2)                 #---Coordenada X do olho na borda de 15m
theta_eye = np.arctan2(y_eye, x_eye)                #---Ângulo do olho do motorista

#---Interseção do Raio 1 (saída) com o círculo de 15m (Encontrado via Delta da equação do círculo)
dot1 = rx1 * np.cos(ang_out1) + ry1 * np.sin(ang_out1)
t1 = -dot1 + np.sqrt(dot1**2 - (rx1**2 + ry1**2 - R_15**2))
X_int1 = rx1 + t1 * np.cos(ang_out1)
Y_int1 = ry1 + t1 * np.sin(ang_out1)
theta_int1 = np.arctan2(Y_int1, X_int1)

#---Interseção do Raio 2 (saída) com o círculo de 15m
dot2 = rx2 * np.cos(ang_out2) + ry2 * np.sin(ang_out2)
t2 = -dot2 + np.sqrt(dot2**2 - (rx2**2 + ry2**2 - R_15**2))
X_int2 = rx2 + t2 * np.cos(ang_out2)
Y_int2 = ry2 + t2 * np.sin(ang_out2)
theta_int2 = np.arctan2(Y_int2, X_int2)

#---Lógica de Interseção Topológica (Intervalos de Ângulo)
theta_s_min = min(theta_int1, theta_int2)           #---Início da faixa de luz (Spread)
theta_s_max = max(theta_int1, theta_int2)           #---Fim da faixa de luz (Spread)
delta_theta_spread = theta_s_max - theta_s_min      #---Abertura angular total (Total da luz)

delta_theta_olho = L_arco_um / R_15                 #---Abertura angular do olho
theta_e_min = theta_eye - delta_theta_olho / 2      #---Início do olho
theta_e_max = theta_eye + delta_theta_olho / 2      #---Fim do olho

#---Tratando os Casos (a), (b) e (c) com Min/Max
overlap_min = max(theta_s_min, theta_e_min)         #---Pega o maior dos limites inferiores
overlap_max = min(theta_s_max, theta_e_max)         #---Pega o menor dos limites superiores
overlap_theta = max(0.0, overlap_max - overlap_min) #---Medida da interseção (zero se não cruzar)

#---Cálculo da Densidade: Medida da Interseção / Medida Total
if delta_theta_spread > 0:
    densidade = overlap_theta / delta_theta_spread
else:
    densidade = 0.0

#---Cálculo da Luz Total e Atualização do Painel com os 2 Resultados
T_total_perc = (T_frac_in * T_frac_out) * 100.0     #---Transmitância de P1 multiplicada pela de R1
resultado_luz.markdown(
    f"**Luz transmitida total:** {T_total_perc:.1f}% do original<br>"
    f"**Densidade de luz:** {densidade:.4f}",
    unsafe_allow_html=True
)
# ==========================================
# ÁREA PRINCIPAL (Gráfico)
# ==========================================

#---Inicializa o gráfico iterativo
fig = go.Figure()

#---Adiciona a faixa de luz (preenchimento respeitando a curvatura da esfera)
# 1. Cria os pontos do arco entre os ângulos T1 e T2 (50 pontos para a curva ficar suave)
t_arc = np.linspace(T1_calc, T2_calc, 50)
x_arc = R * np.cos(t_arc)
y_arc = R * np.sin(t_arc)

#---2. Constrói o contorno: Início V1 -> Arco de P1 a P2 -> Início V2 -> Volta pro Início V1
x_faixa = [vx1[0]] + list(x_arc) + [vx2[0], vx1[0]]
y_faixa = [vy1[0]] + list(y_arc) + [vy2[0], vy1[0]]

fig.add_trace(go.Scatter(
    x=x_faixa,
    y=y_faixa,
    fill='toself',
    fillcolor='rgba(135, 206, 235, 0.4)',       #---Azul claro (SkyBlue) com 40% de opacidade
    line=dict(color='rgba(255,255,255,0)'),     #---Deixa a linha de borda invisível
    name='Faixa de Luz',
    hoverinfo='skip'                            #---Evita que o mouse mostre dados inúteis no meio da faixa
))

#---Adiciona a Esfera
fig.add_trace(go.Scatter(x=x_circle, y=y_circle, mode='lines', name='Esfera', line=dict(color='royalblue', width=2)))
#---Adiciona o Segmento de Reta Central
#---Adiciona o Segmento de Reta Central
fig.add_trace(go.Scatter(
    x=x_seg,
    y=y_seg,
    mode='lines',
    name='Segmento Central',
    line=dict(color='darkmagenta', width=2) #---Cor magenta escura, traço contínuo
))

#---Adiciona a linha do Asfalto
fig.add_trace(go.Scatter(
    x=x_asfalto,
    y=y_asfalto,
    mode='lines',
    name='Asfalto',
    line=dict(color='black', width=3)       #---Cor preta sólida e espessura 3
))


#---Adiciona o Vetor 1
fig.add_trace(go.Scatter(x=vx1, y=vy1, mode='lines', name='Vetor Incidente 1', line=dict(color='firebrick', width=3)))

#---Adiciona o Ponto P1
fig.add_trace(go.Scatter(x=[px1], y=[py1], mode='markers', name='Ponto P1', marker=dict(color='firebrick', size=12)))

#---Adiciona o Vetor 2 e o Ponto P2
fig.add_trace(go.Scatter(x=vx2, y=vy2, mode='lines', name='Vetor Incidente 2', line=dict(color='orange', width=3)))
fig.add_trace(go.Scatter(x=[px2], y=[py2], mode='markers', name='Ponto P2', marker=dict(color='orange', size=12)))

#---Adiciona o Raio Refratado 1 (Dentro da esfera) e o Ponto Q1
fig.add_trace(go.Scatter(x=[px1, qx1], y=[py1, qy1], mode='lines', name='Vetor Refratado 1', line=dict(color='firebrick', width=3)))
fig.add_trace(go.Scatter(x=[qx1], y=[qy1], mode='markers', name='Ponto Q1', marker=dict(color='firebrick', size=12)))

#---Adiciona o Raio Refratado 2 (Dentro da esfera) e o Ponto Q2
fig.add_trace(go.Scatter(x=[px2, qx2], y=[py2, qy2], mode='lines', name='Vetor Refratado 2', line=dict(color='orange', width=3)))
fig.add_trace(go.Scatter(x=[qx2], y=[qy2], mode='markers', name='Ponto Q2', marker=dict(color='orange', size=12)))
#---Adiciona o Raio Refletido 1 (Dentro da esfera) e o Ponto R1
fig.add_trace(go.Scatter(x=[qx1, rx1], y=[qy1, ry1], mode='lines', name='Vetor Refletido 1', line=dict(color='firebrick', width=3)))
fig.add_trace(go.Scatter(x=[rx1], y=[ry1], mode='markers', name='Ponto R1', marker=dict(color='firebrick', size=12)))

#---Adiciona o Raio Refletido 2 (Dentro da esfera) e o Ponto R2
fig.add_trace(go.Scatter(x=[qx2, rx2], y=[qy2, ry2], mode='lines', name='Vetor Refletido 2', line=dict(color='orange', width=3)))
fig.add_trace(go.Scatter(x=[rx2], y=[ry2], mode='markers', name='Ponto R2', marker=dict(color='orange', size=12)))

#---Adiciona o Raio de Saída 1 (Fora da esfera)
fig.add_trace(go.Scatter(x=[rx1, sx1], y=[ry1, sy1], mode='lines', name='Vetor de Saída 1', line=dict(color='firebrick', width=3)))

#---Adiciona o Raio de Saída 2 (Fora da esfera)
fig.add_trace(go.Scatter(x=[rx2, sx2], y=[ry2, sy2], mode='lines', name='Vetor de Saída 2', line=dict(color='orange', width=3)))

#---Adicionando setas de direção no ponto médio dos vetores
mid_x1 = (vx1[0] + vx1[1]) / 2
mid_y1 = (vy1[0] + vy1[1]) / 2
mid_x2 = (vx2[0] + vx2[1]) / 2
mid_y2 = (vy2[0] + vy2[1]) / 2

#---Seta do Vetor 1 (Vermelho)
fig.add_annotation(
    x=mid_x1, y=mid_y1,                                         #---Ponto onde fica a 'cabeça' da seta (no meio)
    ax=vx1[0], ay=vy1[0],                                       #---Ponto onde fica a 'cauda' (lá no início da reta)
    xref='x', yref='y', axref='x', ayref='y',
    showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
    arrowcolor='firebrick'
)

#---Seta do Vetor 2 (Laranja)
fig.add_annotation(
    x=mid_x2, y=mid_y2,                                         #---Ponto onde fica a 'cabeça' da seta (no meio)
    ax=vx2[0], ay=vy2[0],                                       #---Ponto onde fica a 'cauda' (lá no início da reta)
    xref='x', yref='y', axref='x', ayref='y',
    showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
    arrowcolor='orange'
)

#---Setas dos Vetores Refratados (Internos)
mid_qx1 = (px1 + qx1) / 2
mid_qy1 = (py1 + qy1) / 2
mid_qx2 = (px2 + qx2) / 2
mid_qy2 = (py2 + qy2) / 2

#---Seta do Refratado 1 (Vermelho)
fig.add_annotation(
    x=mid_qx1, y=mid_qy1,                                       #---Cabeça da seta no meio do vetor interno
    ax=px1, ay=py1,                                             #---Cauda presa no Ponto P1
    xref='x', yref='y', axref='x', ayref='y',
    showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
    arrowcolor='firebrick'
)

#---Seta do Refratado 2 (Laranja)
fig.add_annotation(
    x=mid_qx2, y=mid_qy2,                                       #---Cabeça da seta no meio do vetor interno
    ax=px2, ay=py2,                                             #---Cauda presa no Ponto P2
    xref='x', yref='y', axref='x', ayref='y',
    showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
    arrowcolor='orange'
)

#---Setas dos Vetores de Saída (Externos R -> S)
mid_sx1 = (rx1 + sx1) / 2
mid_sy1 = (ry1 + sy1) / 2
mid_sx2 = (rx2 + sx2) / 2
mid_sy2 = (ry2 + sy2) / 2

#---Seta do Saída 1 (Vermelho)
fig.add_annotation(
    x=mid_sx1, y=mid_sy1,                                       #---Cabeça da seta no meio do vetor externo
    ax=rx1, ay=ry1,                                             #---Cauda presa no Ponto R1
    xref='x', yref='y', axref='x', ayref='y',
    showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
    arrowcolor='firebrick'
)

#---Seta do Saída 2 (Laranja)
fig.add_annotation(
    x=mid_sx2, y=mid_sy2,                                       #---Cabeça da seta no meio do vetor externo
    ax=rx2, ay=ry2,                                             #---Cauda presa no Ponto R2
    xref='x', yref='y', axref='x', ayref='y',
    showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
    arrowcolor='orange'
)

#---Setas dos Vetores Refletidos (Internos Q -> R)
mid_rx1 = (qx1 + rx1) / 2
mid_ry1 = (qy1 + ry1) / 2
mid_rx2 = (qx2 + rx2) / 2
mid_ry2 = (qy2 + ry2) / 2

#---Seta do Refletido 1 (Vermelho)
fig.add_annotation(
    x=mid_rx1, y=mid_ry1,                                       #---Cabeça da seta no meio do vetor interno
    ax=qx1, ay=qy1,                                             #---Cauda presa no Ponto Q1
    xref='x', yref='y', axref='x', ayref='y',
    showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
    arrowcolor='firebrick'
)

#---Seta do Refletido 2 (Laranja)
fig.add_annotation(
    x=mid_rx2, y=mid_ry2,                                       #---Cabeça da seta no meio do vetor interno
    ax=qx2, ay=qy2,                                             #---Cauda presa no Ponto Q2
    xref='x', yref='y', axref='x', ayref='y',
    showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
    arrowcolor='orange'
)
#---Configurações de proporção, limites travados em 1300 e grade quadriculada
fig.update_layout(
    xaxis=dict(
        range=[-1300, 1300],
        title="X (μm)",
        dtick=500,                              #---Espaçamento da grade de 500 em 500
        showgrid=True,                          #---Ativa as linhas quadriculadas
        gridcolor='rgba(200, 200, 200, 0.5)',   #---Cor da malha (cinza suave)
        zeroline=False,                         #---Remove a linha forte central do eixo 0
        showline=False                          #---Remove as linhas de contorno do gráfico
    ),
    yaxis=dict(
        range=[-1300, 1300],
        title="Y (μm)",
        scaleanchor="x",
        scaleratio=1,
        dtick=500,                              #---Espaçamento da grade de 500 em 500
        showgrid=True,                          #---Ativa as linhas quadriculadas
        gridcolor='rgba(200, 200, 200, 0.5)',   #---Cor da malha (cinza suave)
        zeroline=False,                         #---Remove a linha forte central do eixo 0
        showline=False                          #---Remove as linhas de contorno do gráfico
    ),
    height=700,
    plot_bgcolor='rgba(250, 250, 250, 1)',      #---Fundo levemente mais branco para o quadriculado destacar
    margin=dict(l=20, r=20, t=40, b=20)
)

#---Renderiza o gráfico na tela
st.plotly_chart(fig, use_container_width=True)

# ==========================================
# SEGUNDO GRÁFICO (Macro Escala - 15m)
# ==========================================
st.title(f"Projeção da Luz a {G} metros")

fig2 = go.Figure()

#---Recalculando as interseções macro para plotagem segura
R_15 = float(G) * 10**6

# Interseção Raio 1 com a distância de 15m
dot1 = rx1 * np.cos(ang_out1) + ry1 * np.sin(ang_out1)
t1 = -dot1 + np.sqrt(dot1**2 - (rx1**2 + ry1**2 - R_15**2))
X_int1 = rx1 + t1 * np.cos(ang_out1)
Y_int1 = ry1 + t1 * np.sin(ang_out1)

# Interseção Raio 2 com a distância de 15m
dot2 = rx2 * np.cos(ang_out2) + ry2 * np.sin(ang_out2)
t2 = -dot2 + np.sqrt(dot2**2 - (rx2**2 + ry2**2 - R_15**2))
X_int2 = rx2 + t2 * np.cos(ang_out2)
Y_int2 = ry2 + t2 * np.sin(ang_out2)

#---Verificação física: O raio reflete para fora do vidro ou fica preso na tinta?
# Um ponto está exposto se o produto escalar com a normal da tinta for >= ao deslocamento da tinta
raio1_livre = (rx1 * nx + ry1 * ny) >= d_offset
raio2_livre = (rx2 * nx + ry2 * ny) >= d_offset

if raio1_livre:
    #---Adiciona o Raio de Saída 1 (Estendido até 15m)
    fig2.add_trace(go.Scatter(
        x=[rx1, X_int1], y=[ry1, Y_int1],
        mode='lines', name='Vetor de Saída 1 (Macro)', line=dict(color='firebrick', width=3)
    ))

if raio2_livre:
    #---Adiciona o Raio de Saída 2 (Estendido até 15m)
    fig2.add_trace(go.Scatter(
        x=[rx2, X_int2], y=[ry2, Y_int2],
        mode='lines', name='Vetor de Saída 2 (Macro)', line=dict(color='orange', width=3)
    ))

#---Adiciona o Arco de 15m (Linha rosa no seu esboço)
# Desenhando o arco do chão (y=0) até uma altura de 2m para cobrir a área de visão
theta_macro = np.linspace(0, np.arcsin((2.0 * 10**6) / R_15), 100)
x_macro_arc = R_15 * np.cos(theta_macro)
y_macro_arc = R_15 * np.sin(theta_macro)

fig2.add_trace(go.Scatter(
    x=x_macro_arc, y=y_macro_arc,
    mode='lines', name='Plano de Recepção ({G}m)', line=dict(color='magenta', width=4)
))

#---Adiciona o Arco do Olho (Marrom, centralizado em 1.2m, plotado por cima do rosa)
# L_arco_cm * 10**4 converte cm para μm. Dividimos pelo R_15 para achar a abertura angular em radianos.
delta_theta_olho = (L_arco_cm * 10**4) / R_15
theta_olho = np.linspace(theta_eye - delta_theta_olho/2, theta_eye + delta_theta_olho/2, 50)

x_olho_arc = R_15 * np.cos(theta_olho)
y_olho_arc = R_15 * np.sin(theta_olho)

fig2.add_trace(go.Scatter(
    x=x_olho_arc, y=y_olho_arc,
    mode='lines', name='Arco Visual (Olho)',
    line=dict(color='saddlebrown', width=7)         #---Cor marrom e mais espessa para se sobrepor bem ao magenta
))

#---Setas dos Vetores de Saída no Gráfico Macro (Apontando para o arco)
mid_macro_x1 = (rx1 + X_int1) / 2
mid_macro_y1 = (ry1 + Y_int1) / 2
mid_macro_x2 = (rx2 + X_int2) / 2
mid_macro_y2 = (ry2 + Y_int2) / 2

#---Seta do Saída 1 Macro (Vermelho)
if raio1_livre:
    fig2.add_annotation(
        x=mid_macro_x1, y=mid_macro_y1,                               #---Cabeça da seta no meio do vetor
        ax=rx1, ay=ry1,                                               #---Cauda presa na origem (R1)
        xref='x', yref='y', axref='x', ayref='y',
        showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
        arrowcolor='firebrick'
    )

#---Seta do Saída 2 Macro (Laranja)
if raio2_livre:
    fig2.add_annotation(
        x=mid_macro_x2, y=mid_macro_y2,                               #---Cabeça da seta no meio do vetor
        ax=rx2, ay=ry2,                                               #---Cauda presa na origem (R2)
        xref='x', yref='y', axref='x', ayref='y',
        showarrow=True, arrowhead=2, arrowsize=0.75, arrowwidth=3,
        arrowcolor='orange'
    )

#---Configurações do gráfico macro (Travando proporção e formatando eixos)
fig2.update_layout(
    xaxis=dict(
        range=[-0.5 * 10**6, (float(G) + 1.0) * 10**6], #---Margem adaptável (16m ou 31m)
        title="Distância",
        tickvals=[0, float(G) * 10**6],                 #---Força exibir apenas 0 e o valor de G
        ticktext=['0', f'{G}m'],                        #---Texto dinâmico na legenda
        showgrid=True, gridcolor='rgba(200, 200, 200, 0.4)', zeroline=False
    ),
    yaxis=dict(
        range=[-0.2 * 10**6, 2 * 10**6],            #---Foco na altura, cobrindo o 1.2m
        scaleanchor="x", scaleratio=1,              #---MUITO IMPORTANTE: Trava a proporção real dos ângulos!
        title="Altura",
        tickvals=[0, 1.2 * 10**6],                  #---Força exibir apenas 0 e 1.2m
        ticktext=['0', '1.2m'],
        showgrid=True, gridcolor='rgba(200, 200, 200, 0.4)', zeroline=False
    ),
    height=350,                                     #---Formato retangular mais achatado (estilo 'caixa verde')
    plot_bgcolor='rgba(250, 250, 250, 1)',
    margin=dict(l=40, r=40, t=40, b=20)
)

st.plotly_chart(fig2, use_container_width=True)