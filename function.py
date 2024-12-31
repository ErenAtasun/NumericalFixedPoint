import numpy as np
import matplotlib.pyplot as plt

def fixed_point_iteration(func_str, x_0, tol, max_iter):
    try:
        import math
        eval_globals = {
            entry: getattr(math, entry)
            for entry in dir(math)
            if not entry.startswith("_")
        }
        func = lambda x: eval(func_str, {"x": x}, eval_globals)
    except Exception as exception:        # Kullanıcıdan alınan fonksiyonun python fonksiyonuna çevirildiği kod, çevirilemezse error döndüdürüyor.
        print(f"Error: {exception}")
        return None

    iter_count = 0
    x_values = [x_0]                # Fixed point iterasyonunun başladığı yer burası, x'in (bütün iterasyon değerlerinin) tutulduğu bir liste oluşturdum.
    while iter_count < max_iter:
        x_next = func(x_0)          # x_i_plus_1 = f(x_i)
        # print(f"Iteration {iter_count + 1}: x = {x_next}") #CK YORUM
        x_values.append(x_next)

        if abs(x_next - x_0) < tol:   # Bulunan değerler farkının toleransdan daha düşük olduğu durumda programı sonlandırılıyor. Bulunan kök döndürülüyor.
            print(f"Root found: {x_next}, Iteration count: {iter_count + 1}") #CK YORUM
            plot_iterations(func, x_values)
            return x_next

        x_0 = x_next  # x'i işlem yapılabilmesi adına sonraki x değerine taşır
        iter_count += 1

    print("Max iteration count reached. Root is not found.")
    plot_iterations(func, x_values)
    return {"iterations": iter_count, "x_value": x_values}

def plot_iterations(func, x_values):    # Grafiğin çizildiği method
    x_min = min(x_values) - 1
    x_max = max(x_values) + 1           # x eksenini minimum ve maksimum değerler arasında çizdiriyor.
    x = np.linspace(x_min, x_max, 500) # çizilen x ekseni üzerinde 500 adet nokta oluşturuyor.
    f = np.array([func(val) for val in x])  # f(x) fonksiyonunu, x ekseni üzerindeki her bir değer ile hesaplanıyor. Sonuçlar np.array ile arraye çevriliyor.

    plt.figure(figsize=(16, 9))             # ekrana yansıtılacak grafiğin birim olarak çözünürlüğü, 1600x900
    plt.plot(x, f, label='f(x)', color='blue')  # f(x) fonksiyonunun grafik üzerinde gösterildiği kod, ben mavi renk kullandım.
    plt.plot(x, x, label='y = x', color='gray', linestyle='dashed') # y = x doğrusunun gösterildiği kod, fixed point methodunun gösteriminde kullanılıyor.

    for i in range(len(x_values) - 1):  # Fixed point methodunun grafik üzerinde gösterimi.
        plt.plot([x_values[i], x_values[i]], [x_values[i], x_values[i + 1]], color='red') # x_0 değerinden (g(x_0)) değerine dik çizgileri çiziyor.
        plt.plot([x_values[i], x_values[i + 1]], [x_values[i + 1], x_values[i + 1]], color='red') # g(x_0) değerinden x_next değerine yatay çizgileri çekiyor.

    plt.scatter(x_values, x_values, color='black', zorder=5)  # Her iterasyondaki x değerlerini siyah noktalarla y=x doğrusu üzerinde işaretliyor
    plt.title('Fixed Point Iteration')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.legend() # Fonksiyonların temsili için
    plt.grid()  # Arka planı grid yaptık
    plt.savefig('output_plot.png') # Grafiği kaydediyoruz.
    #plt.show() #CK YORUM