import { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, Link } from 'react-router-dom';

interface IntroduceData {
  text: string;
  images: string[];
}

function HomePage() {
  const [introduceData, setIntroduceData] = useState<IntroduceData>({
    text: '',
    images: []
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGetData = () => {
    setLoading(true);
    setError(null);

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs[0];
      if (activeTab?.id) {
        chrome.tabs.sendMessage(
          activeTab.id,
          { type: 'GET_INTRODUCE_DATA' },
          (response: IntroduceData) => {
            if (chrome.runtime.lastError) {
              console.error(chrome.runtime.lastError.message);
              setError(`에러: ${chrome.runtime.lastError.message}`);
              setLoading(false);
              return;
            }

            if (response) {
              setIntroduceData(response);
            } else {
              setError('contentScript 응답이 없습니다.');
            }
            setLoading(false);
          }
        );
      } else {
        setError('활성 탭을 찾을 수 없습니다.');
        setLoading(false);
      }
    });
  };

  useEffect(() => {
    handleGetData();
    // eslint-disable-next-line
  }, []);

  return (
    <div style={{ padding: '1rem', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ marginBottom: '1rem' }}>
        <h2>Foodly Search <span style={{ fontSize: '0.6em', color: 'red' }}>beta</span></h2>
      </header>

      <button onClick={handleGetData} style={{ marginBottom: '1rem', padding: '0.5rem 1rem' }}>
        다시 불러오기
      </button>

      {loading && <p>데이터를 불러오는 중...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {!loading && !error && (
        <>
          <div>
            <h3>수집된 텍스트:</h3>
            <pre style={{ whiteSpace: 'pre-wrap' }}>{introduceData.text}</pre>
          </div>

          <div style={{ marginTop: '1rem' }}>
            <h3>수집된 이미지 링크:</h3>
            {introduceData.images.length === 0 ? (
              <p>이미지가 없습니다.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {introduceData.images.map((src, index) => (
                  <li key={index} style={{ marginBottom: '8px' }}>
                    <a
                      href={src}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ textDecoration: 'none', color: '#007bff' }}
                    >
                      {src}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
      <nav style={{ marginBottom: '1rem' }}>
        <Link to="/">Home</Link> | <Link to="/team">제작진</Link>
      </nav>
    </div>
  );
}

function TeamPage() {
  const teamMembers = [
    { name: '김진재', role: '프론트엔드 개발, MLOps' },
    { name: '곽희준', role: 'AI 개발' },
    { name: '김정은', role: 'AI 개발' },
    { name: '오수현', role: 'AI 개발' },
    { name: '윤선웅', role: 'AI 개발' },
    { name: '정민지', role: 'AI 개발' },
  ];

  return (
    <div style={{ padding: '1rem', fontFamily: 'Arial, sans-serif' }}>
      <header style={{ marginBottom: '1rem' }}>
        <h2>제작진</h2>
      </header>

      <div>
        {teamMembers.map((member, idx) => (
          <div key={idx} style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
            <h3 style={{ margin: '0 0 0.5rem 0' }}>{member.name}</h3>
            <p style={{ margin: 0 }}>{member.role}</p>
          </div>
        ))}
      </div>

      <nav style={{ marginBottom: '1rem' }}>
        <Link to="/">Home</Link> | <Link to="/team">제작진</Link>
      </nav>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/team" element={<TeamPage />} />
      </Routes>
    </Router>
  );
}

export default App;