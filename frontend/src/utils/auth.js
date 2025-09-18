// JWT 토큰을 디코드하는 함수
export function decodeJWT(token) {
  try {
    // JWT는 header.payload.signature 형태로 구성됨
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('JWT 디코드 에러:', error);
    return null;
  }
}

// 현재 로그인한 사용자의 정보를 가져오는 함수
export function getCurrentUserFromToken() {
  const token = localStorage.getItem('token');
  if (!token) {
    return null;
  }

  const decoded = decodeJWT(token);
  if (!decoded) {
    return null;
  }

  return {
    email: decoded.sub, // JWT의 subject는 보통 이메일
    exp: decoded.exp,   // 만료 시간
    iat: decoded.iat,   // 발급 시간
    // 다른 필드들은 백엔드에서 포함시킨 내용에 따라 추가
  };
}

// 토큰이 유효한지 확인하는 함수
export function isTokenValid() {
  const token = localStorage.getItem('token');
  if (!token) {
    return false;
  }

  const decoded = decodeJWT(token);
  if (!decoded) {
    return false;
  }

  // 현재 시간과 토큰 만료 시간 비교
  const currentTime = Math.floor(Date.now() / 1000);
  return decoded.exp > currentTime;
}

// 토큰에서 사용자 ID 추출 (이메일을 ID로 사용)
export function getUserIdFromToken() {
  const userInfo = getCurrentUserFromToken();
  return userInfo?.email || null;
}