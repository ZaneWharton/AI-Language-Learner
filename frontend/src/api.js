import axios from "axios";

const API =  axios.create({
    baseURL: "http://localhost:8000"
});

const ACCESS = "access_token";
const REFRESH =  "refresh_token";

//Attach access token
API.interceptors.request.use(cfg =>{
    const token = localStorage.getItem(ACCESS);
    if (token) cfg.headers.Authorization = `Bearer ${token}`;
    return cfg
});

//On 401, refresh and retry
API.interceptors.response.use(
    res => res,
    async err => {
        const original = err.config;
        if (err.response?.status === 401 && !original._retry) {
            original._retry = true;
            const refresh = localStorage.getItem(REFRESH);
            if(refresh) {
                const resp = await API.post(
                    "/auth/refresh",
                    {},
                    {headers: {Authorization: `Bearer ${refresh}`}}
                );
                localStorage.setItem(ACCESS, resp.data.access_token);
                localStorage.setItem(REFRESH, resp.data.refresh_token);
                original.headers.Authorization = `Bearer ${resp.data.access_token}`;
                return API(original)
            }
        }
        return Promise.reject(err)
    }
);

export default API