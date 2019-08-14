#include <iostream>
#include <vector>
#include <chrono>
#include <cmath>
using namespace std;

constexpr int VMAX = 501, VMAX_emb = 3601, time_limit = 9900;
int V, E, V_emb, E_emb;
int G[VMAX][VMAX] = {};
vector<int> G_emb[VMAX_emb];
int ans[VMAX] = {};
int ans_inv[VMAX_emb] = {};

//スコア計算
int calc_score(){
    int score = 0;
    for (int i = 0; i < V_emb; i++){
        int now = ans_inv[i];
        if (now == -1)
            continue;
        for(int next_emb:G_emb[i]){
            int next = ans_inv[next_emb];
            if(next == -1)
                continue;
            score += G[now][next];
        }
    }
    return score / 2;
}
//ノードの入れ替え(V_embでのノード番号)
void swap_node(int a, int b){
    if(ans_inv[a] == -1)
        ans[ans_inv[b]] = a;
    else if(ans_inv[b] == -1)
        ans[ans_inv[a]] = b;
    else
        swap(ans[ans_inv[a]], ans[ans_inv[b]]);
    swap(ans_inv[a], ans_inv[b]);
}

int main(){
    //タイマースタート
	std::chrono::system_clock::time_point  start, end;
	start = std::chrono::system_clock::now();

    //入力をうけとる
    cin >> V >> E;
    for (int i = 0; i < E; i++){
        int u, v, w;
        cin >> u >> v >> w;
        u--, v--;
        G[u][v] += w;
        G[v][u] += w;
    }
    cin >> V_emb >> E_emb;
    for (int i = 0; i < E_emb; i++){
        int a, b;
        cin >> a >> b;
        a--, b--;
        G_emb[a].push_back(b);
        G_emb[b].push_back(a);
    }

    //初期状態をつくる
    for (int i = 0; i < VMAX_emb; i++){
        ans_inv[i] = -1;
    }
    for (int i = 0; i < V; i++){
        ans[i] = i;
        ans_inv[i] = i;
    }

    //焼きなまし
    int now_time = 0, iteration = 0;
    double temp_start = 10., temp_end = 1.;

    //10000 回ランダムに混ぜる
    for(int i=0;i<100000;i++)
        swap_node(rand() % V_emb, rand() % V_emb);

    while (now_time < time_limit){
        now_time = chrono::duration_cast<chrono::milliseconds>(chrono::system_clock::now() - start).count();
        double temp = temp_start + (temp_end - temp_start) * now_time / time_limit;

        //入れ替えるマス
        int a = rand() % V_emb, b = rand() % V_emb;
        if (ans_inv[a] == ans_inv[b])
            continue;
        //スコア計算
        int score_bef = calc_score();
        //入れ替え
        swap_node(a, b);
        //スコア計算
        int score_aft = calc_score();
        int delta_score = score_aft - score_bef;
        double rnd = double(rand()%10000)/10000.;
        double prob = exp(delta_score / temp);
        //棄却→戻す
        if (prob < rnd){
            swap_node(a, b);
        }
        else
            iteration++;

        //iterationN回ごとに状態を出力する
        if(iteration%1000==0){
            for (int i = 0; i < V; i++){
                cout << i + 1 << " " << ans[i] + 1 << '\n';
            }
            iteration++;
        }
    }
    //出力
    for (int i = 0; i < V; i++){
        cout << i + 1 << " " << ans[i] + 1 << endl;
    }

    return 0;
}