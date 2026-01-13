import { GET } from '@/app/api/stocks/route';

describe('/api/stocks', () => {
    it('is a function', () => {
        expect(typeof GET).toBe('function');
    });
});
