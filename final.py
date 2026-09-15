import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS

st.set_page_config(page_title="한국남부발전 설비감독 고민 상담방", page_icon="⚡", layout="centered")

# [설정] 코드 내부에 API Key를 고정하여 QR 접속 시 바로 사용 가능하도록 설정합니다.
# "1234" 대신 실제 발급받으신 Upstage API Key 문자열을 입력해 두세요.
DEFAULT_API_KEY = "up_l9akpnqTddTFp7iT5Oe7MUB4b6CGi" 

st.markdown("""
    <style>
    .stApp {
        background-color: transparent !important;
    }

    .bg-slider {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -999;
        background-color: #f5f8fa;
    }

    .bg-slide {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-size: cover;
        background-position: center;
        opacity: 0;
        animation: crossfade 18s infinite;
    }

    .bg-slide::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(255, 255, 255, 0.70);
    }

    .bg-slide:nth-child(1) {
        background-image: url('https://images.unsplash.com/photo-1466611653911-95081537e5b7?q=80&w=2000&auto=format&fit=crop');
        animation-delay: 0s;
    }
    .bg-slide:nth-child(2) {
        background-image: url('https://images.unsplash.com/photo-1508514177221-188b1c77eca2?q=80&w=2000&auto=format&fit=crop');
        animation-delay: 6s;
    }
    .bg-slide:nth-child(3) {
        background-image: url('https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?q=80&w=2000&auto=format&fit=crop');
        animation-delay: 12s;
    }

    @keyframes crossfade {
        0% { opacity: 0; }
        8% { opacity: 1; }
        25% { opacity: 1; }
        33% { opacity: 0; }
        100% { opacity: 0; }
    }

    .header-container {
        text-align: center;
        padding: 1rem 1rem 2rem 1rem;
        background: transparent;
        animation: slideDown 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    .badge {
        display: inline-block;
        background: linear-gradient(90deg, #004C97, #00A651);
        color: white;
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 10px rgba(0, 76, 151, 0.3);
    }

    .main-title {
        font-size: 2rem;
        font-weight: 900;
        color: #112233;
        margin-bottom: 0;
        word-break: keep-all;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(255, 255, 255, 0.8);
    }

    @media (max-width: 600px) {
        .main-title { font-size: 1.5rem; }
    }

    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.8);
        margin-bottom: 1rem;
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stMarkdown {
        animation: slideUp 0.4s ease-out;
    }
    </style>
    
    <div class="bg-slider">
        <div class="bg-slide"></div>
        <div class="bg-slide"></div>
        <div class="bg-slide"></div>
    </div>

    <div class="header-container">
        <div class="badge">⚡ KOSPO AI 통합 코칭 솔루션</div>
        <div class="main-title">한국남부발전 설비감독 고민 상담방</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ KOSPO 시스템 설정")
st.sidebar.info("📌 QR 접속 모드 적용 완료\n(API Key 자동 연동 중)")

st.sidebar.divider()
st.sidebar.subheader("🗣️ 상담 모드 선택")
mode = st.sidebar.radio(
    "원하시는 코칭을 선택하세요:",
    ["🛠️ 발전설비 통합 이상 조치 (기술 상담)", "☕ 남부인 직장 생활/고민 상담 (멘토링)"]
)

if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode

if st.session_state.current_mode != mode:
    st.session_state.messages = []
    st.session_state.round = 1
    st.session_state.current_mode = mode
    st.rerun()

st.sidebar.divider()
if st.sidebar.button("🔄 대화 초기화", use_container_width=True, type="primary"):
    st.session_state.messages = []
    st.session_state.round = 1
    st.rerun()

if "messages" not in st.session_state or not st.session_state.messages:
    if mode == "🛠️ 발전설비 통합 이상 조치 (기술 상담)":
        initial_msg = "🎙 **[시스템 MC]** 안녕하십니까, 남부발전 감독님. 현재 현장에 어떤 발전설비 이상이 발생했습니까?"
    else:
        initial_msg = "🎙 **[시스템 MC]** 안녕하십니까, 남부발전 임직원 여러분. 이직, 직장 생활, 인간관계 등 현재 가지고 계신 고민을 편하게 말씀해 주시면, 맞춤형 멘토 패널을 구성하여 토론을 진행하겠습니다."
    
    st.session_state.messages = [{"role": "assistant", "content": initial_msg}]
    st.session_state.round = 1

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("메시지를 입력하세요..."):
    # 설정된 기본 API Key 사용 (1234 입력 시뮬레이션 포함)
    active_api_key = DEFAULT_API_KEY
    
    if not active_api_key or active_api_key == "1234":
        st.warning("⚠️ 유효한 Upstage API Key가 설정되지 않았습니다. 코드 상단의 `DEFAULT_API_KEY` 변수에 실제 키를 입력해 주세요!")
    else:
        client = OpenAI(
            api_key=active_api_key, 
            base_url="https://api.upstage.ai/v1/solar"
        )
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            MAX_ROUNDS = 4 
            is_final_round = (st.session_state.round >= MAX_ROUNDS)
            core_context = prompt 
            
            if mode == "🛠️ 발전설비 통합 이상 조치 (기술 상담)":
                search_context = ""
                
                if is_final_round:
                    with st.spinner("🌐 KOSPO 설비 환경에 맞춘 관련 기술 지식을 참조 중입니다..."):
                        try:
                            search_query = f"{core_context} 발전소 발전설비 트러블슈팅"
                            search_results = DDGS().text(search_query, region="kr-kr", max_results=3)
                            if search_results:
                                for res in search_results:
                                    search_context += f"- {res.get('body', '')}\n"
                        except Exception:
                            search_context = "검색 서버 연결에 실패했습니다."

                with st.spinner("👨‍🔧 설비 전문가 그룹이 분석 중입니다..."):
                    api_messages = []
                    
                    if not is_final_round:
                        mc_prompt = f"""
                        너는 현장 설비감독을 코칭하는 예리한 'MC'이다.
                        사용자가 아무리 구체적인 해결책을 요구하더라도 절대 먼저 해결책을 제시하지 마라.
                        오직 설비 이상에 대해 DCS 트렌드, 정확한 기기/모델명, 현장 검증 상태 중 누락된 것을 파악하기 위해 날카롭고 짧은 '역질문'만 딱 1개 던져라.

                        [답변 형식]
                        🎙 **[시스템 MC]** (누락된 정보를 묻는 짧고 날카로운 역질문 1개)
                        *(반드시 답변 끝에 `[현재 질문 라운드: {st.session_state.round}/{MAX_ROUNDS - 1}]` 라고 표기할 것)*
                        """
                        api_messages.append({"role": "system", "content": mc_prompt})
                        api_messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
                        st.session_state.round += 1
                    else:
                        panel_prompt = f"""
                        너는 발전설비 종합 코칭 시스템이다.
                        아래 검색된 컨텍스트와 너의 자체 지식을 결합하여 [계측제어 전문가], [현장 전문가], [운전원], [안전관리 전문가]로 구성된 패널들이 치열하게 기술 토론을 진행하도록 해라.

                        [참고 컨텍스트]
                        {search_context}

                        [지침]
                        1. **상호 반박 필수**: 각 페르소나는 서로의 의견에 대해 동의하거나 날카롭게 반박해야 하며, 절대로 자기 자신의 주장을 스스로 반박하지 마라.
                        2. **근거의 내재화**: 주장을 펼칠 때 기술적/논리적 근거를 대사 안에 포함해라.
                        3. **행동 묘사 금지**: 괄호 '()'를 사용하여 행동이나 감정을 묘사하지 말고 대사만 출력할 것.

                        [출력 양식]
                        🎙 **[시스템 MC]**: 🔍 현장 상황과 기술 표준을 바탕으로 각 분야 전문가 패널 토론을 시작하겠습니다!

                        🔥 **[제 1라운드: 원인 분석 및 각자의 시각]**
                        - **[계측제어 전문가]**: (대사만 출력)
                        - **[현장 전문가]**: (대사만 출력)
                        - **[운전원]**: (대사만 출력)
                        - **[안전관리 전문가]**: (대사만 출력)

                        🔥 **[제 2라운드: 조치 방향에 대한 기술적 논쟁 (상호 반박)]**
                        - **[계측제어 전문가]**: (다른 패널의 의견에 대한 반박 또는 보완 대사)
                        - **[현장 전문가]**: (다른 패널의 의견에 대한 반박 또는 보완 대사)
                        - **[운전원]**: (다른 패널의 의견에 대한 반박 또는 보완 대사)
                        - **[안전관리 전문가]**: (다른 패널의 의견에 대한 반박 또는 보완 대사)

                        🔥 **[제 3라운드: 최적의 해결책 최종 합의]**
                        - **[계측제어 전문가]**: (최종 합의 대사)
                        - **[현장 전문가]**: (최종 합의 대사)
                        - **[운전원]**: (최종 합의 대사)
                        - **[안전관리 전문가]**: (최종 합의 대사)

                        📋 **[MC 최종 요약]**
                        **💡 최적의 작업 방향 결론**: 전문가들의 3라운드 합의를 바탕으로 남부발전 현장 설비감독이 즉시 실행해야 할 1, 2, 3단계 행동 지침 도출
                        """
                        api_messages.append({"role": "system", "content": panel_prompt})
                        api_messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
                        st.session_state.round = 1

                response = client.chat.completions.create(
                    model="solar-1-mini-chat",
                    messages=api_messages,
                    temperature=0.3
                )
                bot_reply = response.choices[0].message.content.strip()

            else:
                search_context = ""
                
                if is_final_round:
                    with st.spinner("🌐 백그라운드에서 최신 멘토링 사례를 참조 중입니다..."):
                        try:
                            search_query = f"{core_context} 직장인 멘토링 조언"
                            search_results = DDGS().text(search_query, region="kr-kr", max_results=3)
                            if search_results:
                                for res in search_results:
                                    search_context += f"- {res.get('body', '')}\n"
                        except Exception:
                            search_context = "검색 서버 연결에 실패했습니다."
                        
                with st.spinner("☕ 멘토 패널들이 안건을 분석하고 있습니다..."):
                    api_messages = []
                    
                    if not is_final_round:
                        mc_prompt = f"""
                        너는 직장인 고민 상담 프로그램의 사회자 'MC'이다. 
                        절대로 즉시 해결책을 주지 말고, 상황을 더 깊게 파악하기 위해 새로운 핵심 역질문을 딱 1개만 던져라.
                        
                        [답변 형식]
                        🎙 **[시스템 MC]** (상황을 파고드는 예리한 역질문) 
                        *(반드시 답변 끝에 `[현재 질문 라운드: {st.session_state.round}/{MAX_ROUNDS - 1}]` 라고 표기할 것)*
                        """
                        api_messages.append({"role": "system", "content": mc_prompt})
                        api_messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
                        st.session_state.round += 1
                        
                    else:
                        mentor_prompt = f"""
                        너는 직장인 고민 해결을 위한 다중 페르소나 토론 시스템이다. 
                        수집된 안건에 대해 [현실적인 인생 선배], [엄마], [입사 동기]로 구성된 패널들이 입체적으로 토론하도록 해라.

                        [참고 컨텍스트]
                        {search_context}
                        
                        [패널 성향 및 말투 지침 (필수 준수)]
                        1. **[현실적인 인생 선배]**: 직장 선배 느낌으로 툭툭 던지는 현실적인 훈수 투. (~했어, ~해야지, 정신 차려 등 반말과 해요체를 섞어 씀)
                        2. **[엄마]**: 자식을 향한 애틋함과 걱정이 가득 담긴 다정한 반말 투. (~했어?, ~라니까, 아이고 내 새끼 등 완전한 반말 사용)
                        3. **[입사 동기]**: 찐친 동기끼리 속 시원하게 털어놓는 친근하고 거침없는 반말 투. (~잖아, ~지, 미치겠네 등 완전한 편한 반말 사용)
                        4. **상호 반박 필수**: 각 패널은 서로의 의견에 대해 다른 관점으로 반박하거나 보완해야 하며, 자기 자신의 주장을 스스로 반박하지 마라.
                        5. **행동 묘사 금지**: 괄호 '()'를 사용하여 감정이나 행동을 묘사하지 말고 대사만 출력해라.

                        [출력 양식]
                        🎙 **[시스템 MC]**: 🔍 안건이 충분히 구체화되었습니다. 맞춤형 멘토 패널과 토론을 시작하겠습니다!

                        🔥 **[제 1라운드: 각자의 시각과 해결책 제시]**
                        - **[현실적인 인생 선배]**: (대사만 출력)
                        - **[엄마]**: (대사만 출력)
                        - **[입사 동기]**: (대사만 출력)

                        🔥 **[제 2라운드: 서로의 의견에 대한 치열한 반박]**
                        - **[현실적인 인생 선배]**: (다른 패널의 의견에 대한 반박 대사)
                        - **[엄마]**: (다른 패널의 의견에 대한 반박 대사)
                        - **[입사 동기]**: (다른 패널의 의견에 대한 반박 대사)

                        🔥 **[제 3라운드: 최종 합의점 도출 시도]**
                        - **[현실적인 인생 선배]**: (최종 타협안 대사)
                        - **[엄마]**: (최종 타협안 대사)
                        - **[입사 동기]**: (최종 타협안 대사)

                        📋 **[MC 최종 요약]**
                        **최종 결론**: 3라운드 토론을 종합하여 사용자가 취해야 할 3~4가지의 명확하고 실행 가능한 행동 지침 도출
                        """
                        api_messages.append({"role": "system", "content": mentor_prompt})
                        api_messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
                        st.session_state.round = 1

                response = client.chat.completions.create(
                    model="solar-1-mini-chat",
                    messages=api_messages,
                    temperature=0.7
                )
                bot_reply = response.choices[0].message.content.strip()

            st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
