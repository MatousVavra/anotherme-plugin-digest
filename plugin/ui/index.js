function digestPlugin() {
    return {
        loading: true,
        refreshing: false,
        error: '',
        digest: null,

        async init() {
            this.digest = this._empty();
            await this.load();
        },

        _empty() {
            return {
                user_name: 'friend',
                last_mood: null,
                active_projects: [],
                pending_questions: '(nothing pending)',
                people_count: 0,
                conversation_count: 0,
            };
        },

        async load() {
            this.refreshing = true;
            this.error = '';
            try {
                const resp = await AM.fetch('/plugins/digest');
                if (!resp || !resp.ok) {
                    this._fail('Could not load the digest.');
                    return;
                }
                const data = await resp.json();
                this.digest = {
                    user_name: data.user_name || 'friend',
                    last_mood: data.last_mood || null,
                    active_projects: Array.isArray(data.active_projects) ? data.active_projects : [],
                    pending_questions: data.pending_questions || '(nothing pending)',
                    people_count: data.people_count || 0,
                    conversation_count: data.conversation_count || 0,
                };
                this.loading = false;
            } catch (e) {
                this._fail('Could not load the digest.');
            } finally {
                this.refreshing = false;
            }
        },

        _fail(message) {
            if (this.loading) {
                this.error = message;
                this.loading = false;
            } else {
                AM.toast(message, 'error');
            }
        },
    };
}
