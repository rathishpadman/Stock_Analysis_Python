import { GET } from '@/app/api/weekly/route';
import { GET as GET_MONTHLY } from '@/app/api/monthly/route';
import { GET as GET_SEASONALITY } from '@/app/api/seasonality/route';

describe('/api/weekly', () => {
  it('is a function', () => {
    expect(typeof GET).toBe('function');
  });

  it('returns a Response object', async () => {
    const request = new Request('http://localhost:3000/api/weekly');
    const response = await GET(request);
    
    expect(response).toBeInstanceOf(Response);
  });

  it('returns JSON content type', async () => {
    const request = new Request('http://localhost:3000/api/weekly');
    const response = await GET(request);
    
    expect(response.headers.get('content-type')).toContain('application/json');
  });
});

describe('/api/monthly', () => {
  it('is a function', () => {
    expect(typeof GET_MONTHLY).toBe('function');
  });

  it('returns a Response object', async () => {
    const request = new Request('http://localhost:3000/api/monthly');
    const response = await GET_MONTHLY(request);
    
    expect(response).toBeInstanceOf(Response);
  });

  it('returns JSON content type', async () => {
    const request = new Request('http://localhost:3000/api/monthly');
    const response = await GET_MONTHLY(request);
    
    expect(response.headers.get('content-type')).toContain('application/json');
  });
});

describe('/api/seasonality', () => {
  it('is a function', () => {
    expect(typeof GET_SEASONALITY).toBe('function');
  });

  it('returns a Response object', async () => {
    const request = new Request('http://localhost:3000/api/seasonality');
    const response = await GET_SEASONALITY(request);
    
    expect(response).toBeInstanceOf(Response);
  });

  it('returns JSON content type', async () => {
    const request = new Request('http://localhost:3000/api/seasonality');
    const response = await GET_SEASONALITY(request);
    
    expect(response.headers.get('content-type')).toContain('application/json');
  });
});
